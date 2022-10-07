from lib.creoClass import CreoAsm
from pathlib import Path
import os, logging, pprint

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.disable()

if __name__ == '__main__':

    # Declare basepath and filenames
    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) # Get working directory of file
    os.chdir(BASE_DIR)

    fileName = 'Simple_bom.txt'
    importedBomFile = Path('./BOM_imports/') / Path(fileName)

    # Import BOM file and strip out blank lines
    rows = []
    with open(importedBomFile, 'r') as file_object:
        contents = file_object.readlines()
        for row in contents:
            if row != '\n':
                row.strip()
                rows.append(row)

    # Establish root assembly item" row 1
    rootRow = rows[0]
    rows.pop(0)
    rootRow = rootRow.strip().split(' ')
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
        # logging.debug(f'Row item: {row}')
        # If read row starts with part summary line, exit loop
        if row[0] == 'Summary':
            logging.debug(f'Summary of parts found...\n\n---EXITING LOOP---\n\n')
            break

        # If read row is an assembly
        if row[0] == 'Sub-Assembly':
            logging.debug(f'Assembly Header Identified: {row[0]}, {row[1]}')
            subName = row[1]
            for level in reversed(cTree):
                for iCreoAsm in level.children:
                    if subName == iCreoAsm.name:
                        cParent = iCreoAsm
                        logging.debug(f'Parent set to: {cParent}')
                        cLevel = cParent.level + 1
                        cBOMID = len(cParent.children) + 1
                else:
                    continue

        # If read row is a sub-bom item
        else:
            logging.debug(f'Sub-bom item routine started: {row[2]}, QTY {row[0]}')
            cQTY, cType, cName = row[0:3]
            cNode = CreoAsm(cName, cType, cBOMID, cQTY, 1, parent=cParent)
            cNode.level = cLevel
            cBOMID += 1

    # print(rootNode.children)
    rootNode.printTree()