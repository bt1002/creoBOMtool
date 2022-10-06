from unicodedata import name
from lib.creoClass import CreoAsm
from pathlib import Path
import os, logging, pprint

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable()

# from anytree import CreoAsm, RenderTree

# Declare basepath and filenames
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) # Get working directory of file
os.chdir(BASE_DIR)

fileName = 'Simple_bom.txt'
importedBomFile = Path('./BOM_Imports/') / Path(fileName)

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

rootNode = CreoAsm(rootRow[1], 'A', 1, 1, 0)

cLevel = 1
cBOMID = 1

i = 0
# Establish root assembly tree, clean up rows afterwards
for row in rows:
    i += 1
    if row[0].lower() in ['a', 's']:  # If first item in row is not a digit
        break
    else:
        row = row.split()
        cQTY, cType, cName = row[0:3]
        cNode = CreoAsm(cName, cType, cBOMID, cQTY, 1, parent=rootNode)
        cBOMID += 1
del rows[:i-1]

# Set index for row increments
cLevel = 2
cBOMID = 1
cTree = [rootNode]

for row in rows:
    if row[0].lower() in ['a', 's']:  # If first item in row is not a digit
        row = row.strip().split(' ')
        if row[0] in 'Sub-Assembly':  # If first word in line is Assembly
            logging.debug(f'Assembly identified: {row[0]}')

        if row[0] in 'Summary':  # If first word in row is Summary - start of imported BOM rollup
            logging.debug(f'Summary identified: {row[0]}')
    else: ##### THIS IS CURRENTLY BROKEN, NEED TO ADD LOGIC FOR WALKING UP CTREE AND INITIALIZATION
        # logging.debug('Start else statement')
        cQTY, cType, cName = row[0:3]
        cNode = CreoAsm(cName, 'P', cBOMID, cQTY, cLevel)
        for node in cTree:
            logging.debug(f'Level 1: for {node} in {cTree}:')
            logging.debug(print(node.children))
            for child in node.children:
                logging.debug(f'Level 2.1: for {child} in {node.children}')
                childNames = []
                for names in child:
                    childNames.append(child.name)
                logging.debug(f'Level 2.2: cName: {cName}, childNames {childNames}')
                if cName in childNames:
                    cNode.parent = child
                    break

# print(rootNode.children)
rootNode.printTree()



# Identify header lines and sub-bom items
# pprint.pprint(rows)

# if __name__ == '__main__':

#     # Declare root
#     root = CreoAsm(id='AsmRoot000')

#     # Add parts
#     subAsm010 = CreoAsm(id='SubAsm010', parent=root)
#     subAsm020 = CreoAsm(id='subAsm020', parent=root)
#     subAsm030 = CreoAsm(id='subAsm030', parent=root)
#     part011 = CreoAsm(id='part011', parent=subAsm010)
#     part012 = CreoAsm(id='part020', parent=subAsm010)
#     part021 = CreoAsm(id='part021', parent=subAsm020)

#     # Print Tree
#     root.printTree()

#     # print(RenderTree(root))


# # Read file and import
