from lib.creoClass import CreoAsm
from pathlib import Path
import os, logging, pprint

logname = 'bom_import_log.txt'
logging.basicConfig(filename=logname, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
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
    rootID = f'{rootRow[1]}.A.0.0'

    rootNode = CreoAsm(rootRow[1], rootRow[0], 1, 1, 0)

    cLevel = 1
    cBOMID = 1

    # Set index for row increments
    cLevel = 1
    cBOMID = 1
    cTree = [rootNode]
    cParent = cTree[-1]

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
            logging.debug(f'Length of Tree: {len(cTree)}')
            subName = row[1]
            for level in reversed(cTree):
                for iCreoAsm in level.children:
                    if subName == iCreoAsm.name:
                        cParent = iCreoAsm
                        cLevel = cParent.level + 1
                        cBOMID = len(cParent.children) + 1
                        cTree = cTree[:cLevel+1]
                        # logging.debug(f'Parent set to XXX: {cParent}')
                        logging.debug(f'New Parent Level: {cParent.level}')
                        logging.debug(f'New Current Level: {cLevel}')
                        logging.debug(f'New length of Tree: {len(cTree)}')
                else:
                    continue

        # If read row is a sub-bom item
        else:
            logging.critical(f'Sub-bom item routine started: {row[2]}, QTY {row[0]}')
            cQTY, cType, cName = row[0:3]
            cNode = CreoAsm(cName, cType, cBOMID, cQTY, 1, parent=cParent)
            cNode.level = cLevel
            cBOMID += 1
            # print(cNode.name)
            if cType == 'Sub-Assembly':
                # logging.debug(f'Asm Level {cParent.level}')
                # logging.debug(f'cLevel: {cLevel}')
                if cLevel > len(cTree):
                    logging.debug(f'Current Asm Level: {cLevel} Current Tree Level: {len(cTree)}')
                    cTree.append(cParent)
                    logging.debug(f'New Length of Tree: {cTree}')



    # rootNode.printTree()