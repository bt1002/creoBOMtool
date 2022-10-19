import os
from pathlib import Path

# Filename declarations
LOG_FILE = Path("LOG_creoBOMtool.py.txt")

# Get current working directory
CONST_PATH = Path(
    os.path.dirname(os.path.abspath(__file__))
)  # Get working directory of file
ROOT_DIR = CONST_PATH.parent
os.chdir(ROOT_DIR)

# Folder locations for data
EXPORT_DIR = ROOT_DIR / Path("./exports")
LOG_DIR = ROOT_DIR / Path("./logs")
IMPORT_DIR = ROOT_DIR / Path("./creo_bom_imports")
IMAGES_DIR = ROOT_DIR / Path("./creo_images")
JSON_EXP_DIR = EXPORT_DIR
MERGED_BOM_EXP_DIR = EXPORT_DIR
XLS_EXP_DIR = EXPORT_DIR

LOG_PATH = LOG_DIR / LOG_FILE

if __name__ == '__main__':
    exit()
