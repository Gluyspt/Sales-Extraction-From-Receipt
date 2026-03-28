from pathlib import Path
from typing import List, Union
import cv2
import re
from paddleocr import PaddleOCR
from difflib import get_close_matches
from collections import defaultdict
import config

print(f"Initializing PaddleOCR with '{config.OCR_LANG}' model...")
try:
    ocr = PaddleOCR(lang=config.OCR_LANG) 
except Exception as e:
    print(f"Fatal error during initialization: {e}")
    raise


def process_ocr(image: Union[str, Path], recipes_name: List[str]):
    """
    returns:
    0: OCR failure or processing error
    1: OCR success and CSV saved
    2: no text detected
    """
    # Define Regex Filters
    price_regex = re.compile(r'^\d+\.\d{2}$') 
    total_keywords = ['total qty', 'ยอดรวม', 'vat', 'credit card']

    # Regex to find explicit QTY-Name structure (starts with QTY + separator)
    explicit_qty_name_regex = re.compile(r'^\s*([\d\s×x]+)\s*[:.]\s*(.*)')

    # Regex to check if a line is just a quantity or separator
    standalone_qty_regex = re.compile(r'^\s*([\d\s×x]+)\s*$') 

    try:
        result = ocr.predict(input=str(image))
        if not result[0]:
            return 2, ['','']

        result_data = result[0]
        
        # Layout Detection
        y_start_pixel = 99999
        y_end_pixel = 99999
        for poly, text, score in zip(result_data['rec_polys'], result_data['rec_texts'], result_data['rec_scores']):
            text_clean = text.strip().lower()
            current_y_top = poly[:, 1].min()
            if price_regex.match(text_clean):
                if current_y_top < y_start_pixel: y_start_pixel = current_y_top
            if any(keyword in text_clean for keyword in total_keywords):
                if current_y_top < y_end_pixel: y_end_pixel = current_y_top
        Y_START = y_start_pixel - 10
        Y_END = y_end_pixel - 10
        if Y_START > 9000: Y_START = 0 
        if Y_END > 9000: Y_END = 2000 

        # Clear unecessary data
        image = cv2.imread(str(image))
        if image is None:
            print(f"Error: Could not decode image {image}")
            return 0
        
        raw_item_list = [] 
        for poly, text, score in zip(result_data['rec_polys'], result_data['rec_texts'], result_data['rec_scores']):
            text = text.strip()
            avg_y = poly[:, 1].mean()
            if not (Y_START < avg_y < Y_END): continue 
            if price_regex.match(text): continue 
            if 'total qty' in text.lower(): continue
            if re.fullmatch(r'^[x×:.]+$', text): continue 
            if not re.search(r'[ก-ฮa-zA-Z\d]', text): continue
                
            raw_item_list.append({'text': text, 'poly': poly})

        # Pair Qty and Name, then Fuzzy match and correct
        aggregated_items = defaultdict(int) 

        i = 0
        while i < len(raw_item_list):
            current_item = raw_item_list[i]
            text = current_item['text']
            poly = current_item['poly']
            
            # Start a list to hold boxes for this specific menu item
            # If it's just one line, this list will have 1 box.
            # If we find a qty on the next line, we will add that box to this list.
            
            qty = 1 
            name_to_check = text
            
            # Check for explicit QTY-NAME (1 :เป็ปชี่)
            explicit_match = explicit_qty_name_regex.match(text)
            if explicit_match:
                raw_qty_part = explicit_match.group(1).strip()
                name_to_check = explicit_match.group(2).strip()
                
                qty_numbers = re.findall(r'\d+', raw_qty_part)
                if qty_numbers:
                    qty = int(qty_numbers[0])
                
            # Check for name only structure ('หมูคารูบิคุโรบตะ 2' followed by '1')
            elif ':' not in text and '×' not in text:
                
                # 1. Check embedded trailing quantity
                trailing_qty_match = re.search(r'\s(\d+)$', text)
                if trailing_qty_match:
                    qty = int(trailing_qty_match.group(1))
                    name_to_check = text[:trailing_qty_match.start()].strip()
                else:
                    name_to_check = text
                    qty = 1
                    
                # 2. Check the next line for a standalone quantity
                if i + 1 < len(raw_item_list):
                    next_item = raw_item_list[i + 1]
                    next_item_text = next_item['text']
                    standalone_match = standalone_qty_regex.match(next_item_text)
                    
                    if standalone_match:
                        qty_numbers = re.findall(r'\d+', standalone_match.group(1))
                        if qty_numbers:
                            qty = int(qty_numbers[0]) 
                        
                        i += 1 # Skip the next line since we used it as quantity

            # Fuzzy matching and name correction
            name_to_check = re.sub(r'[\d\s×x]+$', '', name_to_check).strip()

            matches = get_close_matches(name_to_check, recipes_name, n=1, cutoff=config.FUZZY_MATCH_CUTOFF) 

            corrected_name = None
            if matches:
                corrected_name = matches[0]

            if corrected_name and len(name_to_check) > 2:
                aggregated_items[corrected_name] += qty
            
            i += 1

        # Save results 
        # send out the result as a list qty and name
        # output_dir = os.path.dirname(output_csv_file)
        # if output_dir:
        #     os.makedirs(output_dir, exist_ok=True)

        # with open(output_csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(['Quantity', 'Menu Name'])
        #     for name, qty in aggregated_items.items():
        #         writer.writerow([str(qty), name])
        
        result = []
        for name, qty in aggregated_items.items():
            result.append([str(qty), name])
        return 1, result

    except Exception as e:
        print(f"An error occurred during processing: {e}")
        return 0, ['','']