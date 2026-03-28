# Sales-Extraction-From-Receipt
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

An automated pipeline that watches a folder for incoming receipt scans, extracts order data using OCR, fuzzy-matches item names against a recipe list, and outputs structured CSV files.

---

## How It Works

```
scans/incoming/  →  scans/processing/  →  scans/done/
                          ↓
                       ocr.py
                          ↓
                    output_csv/YYYY_MM_DD/N.csv
```

1. A scanner (or any process) drops an image into `scans/incoming/`
2. The file watcher picks it up and moves it to `scans/processing/`
3. PaddleOCR reads the receipt and extracts text
4. Each item is fuzzy-matched against `recipes/recipes_name.csv`
5. Matched items and quantities are saved to `output_csv/YYYY_MM_DD/N.csv`
6. The image is moved to `scans/done/` on success, or `scans/failed/` on failure

---

## Project Structure

```
project_directory/
├── scans/
│   ├── incoming/       # ⭐ Drop scans here ⭐
│   ├── processing/     # Temporary — files being processed
│   ├── done/           # Successfully processed images
│   └── failed/         # Images that failed OCR after max retries
├── output_csv/         # OCR results, organized by date
├── recipes/
│   └── recipes_name.csv  # One recipe/menu name per row
├── logs/               # Rotating daily logs
├── config.py           # All settings in one place
├── pipeline.py         # Main entry point — watcher + worker
├── ocr.py              # OCR logic and fuzzy matching
├── cleanup.py          # Deletes files older than retention limit
├── main.py
└── requirements.txt
```

---

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Add your menu names**

Create `recipes/recipes_name.csv` with one item per row:
```
ข้าวผัด
ต้มยำกุ้ง
ผัดไทย
```

**3. Configure settings in `config.py`**

| Setting | Default | Description |
|---|---|---|
| `OCR_LANG` | `th` | OCR language (PaddleOCR language code) |
| `FUZZY_MATCH_CUTOFF` | `0.6` | Match confidence threshold (0.0–1.0) |
| `MAX_RETRIES` | `3` | Retry attempts before marking as failed |
| `RETENTION_DAYS` | `30` | Days to keep files before cleanup deletes them |

**4. Run**
```bash
python main.py
```

---

## Output Format

Each processed receipt produces a CSV at `output_csv/YYYY_MM_DD/N.csv`:

```
Quantity,Recipe Name
2,ข้าวผัด
1,ต้มยำกุ้ง
```

---

## Logs

Logs are written to `logs/` and rotate daily.

- Active log: `logs/current.log`
- Archived logs: `logs/YYYY_MM_DD.log`
- Retention: 30 days (configurable via `RETENTION_DAYS`)

---

## Notes

- Supported 106 language based from PaddleOCR (PP-OCRv5) including Thai, English, Chinese, Japanese, Korean, French, Arabic, and more.
Visit the [PaddleOCR GitHub Repository](https://github.com/PaddlePaddle/PaddleOCR?tab=readme-ov-file#-license) for more information.

- Supported image formats: `.jpg`, `.jpeg`, `.png`, `.pdf`
- If the pipeline crashes, any files left in `scans/processing/` are automatically re-queued on next startup
- Cleanup runs automatically every 24 hours while the pipeline is running

# 📄 License
```
This project is released under the Apache 2.0 license.
```

# 🎓 Citation

**Repository:**
```bibtex
@misc{paddleocr2020,
  title={PaddleOCR: Awesome Multilingual OCR Toolkits based on PaddlePaddle},
  author={PaddlePaddle Authors},
  year={2020},
  howpublished={\url{https://github.com/PaddlePaddle/PaddleOCR}},
}
```
