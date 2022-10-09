from lib.creoClass import CreoAsm
from pathlib import Path
import os, logging, pprint
import pyinputplus as pyip
import numpy as np
from numpy import *

logname = 'bom_import_log.txt'
logging.basicConfig(filename=logname, level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.disable()

# Declare basepath and filenames
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) # Get working directory of file
os.chdir(BASE_DIR)

fileName = 'chassis-000.bom'
importedBomFile = Path('./BOM_imports/') / Path(fileName)

rows = []
with open(importedBomFile, 'r', encoding='utf-8-sig') as file_object:
    contents = file_object.readlines()
    for row in contents:
        if row != '\n':
            row.strip()
            rows.append(row)

full_asm_names = []
with open('temp.txt', 'w') as fileObject:
    for row in rows:
        row = row.split()
        a = str(row[0])
        b = str(row[1])
        # c = str(row[2])
        # fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')
        if a[:3] == 'Sub':
            fileObject.write(f'{a.ljust(15," ")} {b.ljust(8," ")}\n')
            full_asm_names.append(b)

unique_asm_names = []
unique_asm_counts = []

# print(full_asm_names)

for asm_name in full_asm_names:
    if asm_name not in unique_asm_names:
        unique_asm_names.append(asm_name)
        unique_asm_counts.append(1)
    else:
        index = unique_asm_names.index(asm_name)
        unique_asm_counts[index] = unique_asm_counts[index] + 1

with open('temp2.txt', 'w') as fileObject:
    for i in range(len(unique_asm_names)):
        count = unique_asm_counts[i]
        names = unique_asm_names[i]
        fileObject.write(f'{str(count).ljust(4," ")} {names.ljust(32," ")}\n')