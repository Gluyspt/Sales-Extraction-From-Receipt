import os

# --- BASE DIRECTORY ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_abs_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)

# --- FOLDER PATHS ---
INCOMING_FOLDER = get_abs_path("scans/incoming")
PROCESSING_FOLDER = get_abs_path("scans/processing")
DONE_FOLDER = get_abs_path("scans/done")
OUTPUT_FOLDER = get_abs_path("output_csv")
FAILED_FOLDER = get_abs_path("scans/failed")
LOG_FOLDER = get_abs_path("logs")
RECIPES_NAME = get_abs_path("recipes/recipes_name.csv")

# --- FILE PATHS ---
RECIPES_NAME = get_abs_path("recipes/recipes_name.csv")

# --- APP SETTINGS ---
MAX_RETRIES = 3
RETENTION_DAYS = 30
# You can add ocr settings here too if you update ocr.py to import config
OCR_LANG = 'th'
FUZZY_MATCH_CUTOFF = 0.6