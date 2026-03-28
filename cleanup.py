import os
import re
import shutil
import logging
from datetime import datetime
import time

# --- CONFIGURATION ---
FOLDERS_TO_CLEAN = ["output_csv", "scans/done", "scans/failed"]
RETENTION_DAYS = 30

RECIPES_FOLDER = "recipes"
ROOT_FOLDER = "." # This is the main \munchbox_ocr folder

logger = logging.getLogger("MunchBox")

def get_date_from_filename(filename):
    """
    Looks for YYYY_MM_DD in the filename.
    Example: 2026_03_28_receipt1.csv -> returns datetime object
    """
    match = re.search(r'(\d{4})_(\d{2})_(\d{2})', filename)
    if match:
        try:
            return datetime.strptime(match.group(0), '%Y_%m_%d')
        except ValueError:
            return None
    return None

def run_cleanup():
    """
    Scans folders and deletes files older than RETENTION_DAYS 
    using the system's 'Last Modified' timestamp.
    """
    cutoff_seconds = time.time() - (RETENTION_DAYS * 24 * 60 * 60)
    files_deleted = 0
    files_rescued = 0
    
    logger.info(f"[CLEANUP] Task started. Looking for files older than {RETENTION_DAYS} days...")

    for folder in FOLDERS_TO_CLEAN:
        if not os.path.exists(folder): 
            continue

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)

            # --- 1. SAFETY CHECKS (Now inside the loop) ---
            # 1. Skip the active log (avoid crash)
            if filename == "current.log":
                continue
            
            # 2. If it's the recipe file, move it to \recipes
            if "recipes_name" in filename.lower():
                try:
                    shutil.move(file_path, os.path.join(RECIPES_FOLDER, filename))
                    logger.warning(f"[RESCUE] Found misplaced recipe {filename}. Moved to {RECIPES_FOLDER}")
                    files_rescued += 1
                except Exception as e:
                    logger.error(f"[RESCUE ERROR] Could not move {filename}: {e}")
                continue
            
            # 3. If it's a python script, move it to the root folder
            if filename.endswith(".py"):
                try:
                    shutil.move(file_path, os.path.join(ROOT_FOLDER, filename))
                    logger.warning(f"[RESCUE] Found misplaced script {filename}. Moved to Root.")
                    files_rescued += 1
                except Exception as e:
                    logger.error(f"[RESCUE ERROR] Could not move {filename}: {e}")
                continue
            
            # --- 2. DELETE LOGIC (Age Check) ---
            if os.path.isfile(file_path):
                if os.path.getmtime(file_path) < cutoff_seconds:
                    try:
                        os.remove(file_path)
                        files_deleted += 1
                    except Exception as e:
                        logger.error(f"[CLEANUP] Failed to delete {filename}: {e}")

    if files_deleted > 0:
        logger.info(f"[CLEANUP] Removed {files_deleted} expired files.")
    else:
        logger.info("[CLEANUP] No expired files found.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_cleanup()