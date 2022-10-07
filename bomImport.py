from lib.creoClass import CreoAsm
from pathlib import Path
import os, logging, pprint
import pyinputplus as pyip

logname = 'bom_import_log.txt'
logging.basicConfig(filename=logname, level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.disable()

# Declare basepath and filenames
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) # Get working directory of file
os.chdir(BASE_DIR)

fileName = 'chassis-000.bom'
importedBomFile = Path('./BOM_imports/') / Path(fileName)

if __name__ == '__main__':

    # Import BOM file and strip out blank lines
    rows = []
    with open(importedBomFile, 'r', encoding='utf-8-sig') as file_object:
        contents = file_object.readlines()
        for row in contents:
            if row != '\n':
                row.strip()
                rows.append(row)

    # Establish root assembly item" row 1
    rootRow = rows[0]
    rows.pop(0)
    rootRow = rootRow.strip().split()
    rootID = f'{rootRow[1]}.{rootRow[0]}.0.0'

    rootNode = CreoAsm(rootRow[1], rootRow[0], 1, 1, 0)
    logging.critical(f'Assembly Node Created: {rootRow[0]}, {rootRow[1]}')

    cLevel = 1
    cBOMID = 1

    # cTree = [rootNode]
    cParent = rootNode

    for row in rows:
        row = row.strip().split()
        # If read row starts with part summary line, exit loop
        if row[0] == 'Summary':
            logging.critical(f'Summary of parts found...\n\n---EXITING LOOP---\n\n')
            break

        # If read row is an assembly
        if row[0] == 'Sub-Assembly':
            logging.critical(f'Assembly Header Identified: {row[0]}, {row[1]}')
            logging.debug(f'Parent Level: {cParent.level}')
            logging.debug(f'Current Level: {cLevel}')
            subName = row[1]
            for level in cParent.iter_path_reverse():
                for branch in level.children:
                    if subName == branch.name:
                        cParent = branch
                        cLevel = cParent.level + 1
                        cBOMID = len(cParent.children) + 1
                        logging.debug(f'New Parent {level.name} to {branch.name}, Level: {cParent.level}')
                        logging.critical(f'\n\n{cParent.getParents()}\n')
                        logging.debug(f'New Current Level: {cLevel}')
                else:
                    continue

        # If read row is a sub-bom item
        else:
            logging.critical(f'Sub-bom item routine started: {row[2]}, QTY {row[0]}')
            cQTY, cType, cName = row[0:3]
            cNode = CreoAsm(cName, cType, cBOMID, cQTY, 1, parent=cParent)
            cNode.level = cLevel
            cBOMID += 1
    rootNode.printTree(2)

    # while True:
    #     print('Print Input: ', end='')
    #     userInput = pyip.inputStr()
    #     rootNode.printTree(userInput)