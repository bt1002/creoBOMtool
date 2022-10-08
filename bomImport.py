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
# fileName = 'gpu-tray-rivet.bom'
importedBomFile = Path('./BOM_imports/') / Path(fileName)

def buildDataModel(filePath):
    # Import BOM file and strip out blank lines
    rows = []
    print(f'Importing file: {BASE_DIR}\{importedBomFile}')
    with open(importedBomFile, 'r', encoding='utf-8-sig') as file_object:
        contents = file_object.readlines()
        for row in contents:
            if row != '\n':
                row.strip()
                rows.append(row)

    # Establish root assembly item" row 1
    print('Building Root Row...')
    rootRow = rows[0]
    rows.pop(0)
    rootRow = rootRow.strip().split()
    rootID = f'{rootRow[1]}.{rootRow[0]}.0.0'

    rootNode = CreoAsm(name=rootRow[1], type=rootRow[0], bomID=1, qty=1)
    logging.critical(f'Assembly Node Created: {rootRow[0]}, {rootRow[1]}')

    cLevel = 1
    cBOMID = 1
    cParent = rootNode

    # Iterate file rows looking for Assemblies or Parts and create 'Nodes'
    print('Parsing BOM...')
    summaryRowStart = 0
    index = 0
    for row in rows:
        row = row.strip().split()
        # If read row starts with part summary line, exit loop
        if row[0] == 'Summary':
            logging.critical(f'Summary of parts found...row: {index}\n---EXITING LOOP---')
            summaryRowStart = index + 1
            break

        # If read row is an assembly, iterate from bottom of tree upwards looking for a part name match in higher level parent
        # First part name found in upper level will be assigned as the new parent item and add following items as children
        elif row[0] == 'Sub-Assembly':
            logging.debug(f'Assembly Header Identified: {row[0]}, {row[1]}')
            logging.debug(f'Parent Level: {cParent.depth}')
            logging.debug(f'Current Level: {cLevel}')
            subName = row[1]
            for level in cParent.iter_path_reverse():
                for branch in level.children:
                    if subName == branch.name:
                        cParent = branch
                        cLevel = cParent.depth + 1
                        cBOMID = len(cParent.children) + 1
                        logging.debug(f'New Parent {level.name} to {branch.name}, Level: {cParent.depth}')
                        logging.debug(f'\n\n{cParent.printParents()}\n')
                        logging.debug(f'New Current Level: {cLevel}')
                else:
                    continue

        # If read row is a sub-bom item, create node of parts and assign parent and part properties
        else:
            logging.debug(f'Sub-bom item routine started: {row[2]}, QTY {row[0]}')
            cQTY, cType, cName = row[0:3]
            cNode = CreoAsm(cName, cType, cBOMID, cQTY, parent=cParent)
            cBOMID += 1
        index += 1

    # Output list of summary from BOM import
    logging.critical(f'Starting Part Summary')
    summaryRows = rows[summaryRowStart:]
    bomSummaryQTY = []
    bomSummaryType = []
    bomSummaryName = []
    for row in summaryRows:
        row = row.strip().split()
        bomSummaryQTY.append(int(row[0]))
        bomSummaryType.append(row[1])
        bomSummaryName.append(row[2])
    bomSummary = [bomSummaryQTY, bomSummaryType, bomSummaryName]
    # pprint.pprint(bomSummary)

    # Crease list of items for calculated unique part items
    logging.critical(f'Calculating BOM')
    allLeaves = rootNode.searchLeaves()

    # Set extended quantities for each branch
    for leaf in allLeaves:
        leaf.setBranchQTY()

    # Create unmered BOM tree list for branch quantities
    leafQTY = []
    leafType = []
    leafName = []
    for leaves in allLeaves:
        leafQTY.append(leaves.branchQTY)
        leafType.append(leaves.type)
        leafName.append(leaves.name)
    unmergedBOM = [leafQTY, leafType, leafName]

    ####### DEBUG CODE ########
    np_unmergedBOM = np.array(unmergedBOM)
    np_unmergedBOM = np_unmergedBOM.transpose()
    np_unmergedBOM = np_unmergedBOM[np_unmergedBOM[:,2].argsort()]
    # pprint.pprint(np_unmergedBOM)

    with open('unmerged_mergedBOM.txt', 'w') as fileObject:
        for i in np_unmergedBOM:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            # fileObject.write(f'{a.ljust*(10,"_")}{b.ljust*(10,"_")}{c.ljust*(10,"_")}+"\n"')
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')

    # Create merged list of BOM items with full tree quantities for each unique part
    mergedQTY = []
    mergedType = []
    mergedName = []
    for i in range(len(leafName)):
        if unmergedBOM[2][i] not in mergedName:  # If partname not in merged bom
            mergedQTY.append(unmergedBOM[0][i])
            mergedType.append(unmergedBOM[1][i])
            mergedName.append(unmergedBOM[2][i])
        else:
            for j in range(len(mergedName)):
                if unmergedBOM[2][i] == mergedName[j]:
                    temp = mergedQTY[j]
                    mergedQTY[j] = mergedQTY[j] + unmergedBOM[0][i]
                    print(f'merging {mergedName[j]}: {unmergedBOM[0][i]} + {temp} to {mergedQTY[j]}')
    mergedBOM = [mergedQTY, mergedType, mergedName]
    
    np_mergedBOM = np.array(mergedBOM)
    np_mergedBOM = np_mergedBOM.transpose()
    np_mergedBOM = np_mergedBOM[np_mergedBOM[:,2].argsort()]
    # pprint.pprint(np_mergedBOM)

    np_bomSummary = np.array(bomSummary)
    np_bomSummary = np_bomSummary.transpose()
    np_bomSummary = np_bomSummary[np_bomSummary[:,2].argsort()]

    with open('np_un-mergedBOM.txt', 'w') as fileObject:
        for i in np_unmergedBOM:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')

    with open('np_mergedBOM.txt', 'w') as fileObject:
        for i in np_mergedBOM:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')

    with open('np_bomSummary.txt', 'w') as fileObject:
        for i in np_bomSummary:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')

    # comparison = np_mergedBOM == np_bomSummary
    # # print(comparison)
    # try:
    #     equal_arrays = comparison.all()
    # except:
    #     print('BOM check failed')
    # print(f'Completed BOM check: {equal_arrays}')

    print('Completed tree build.')
    return rootNode

def searchPart(part):
    '''Searches input node for parts with ID'''
    userInput = pyip.inputStr('Enter Part Name (enter "q" for quit):  ')
    if userInput == 'q':
        return
    else:
        creoParts = part.searchTree(userInput)
        partNames = []
        partPath = []
        for part in creoParts:
            partNames.append(part.name)
            partPath.append(part.printParents())
        searchResults = [creoParts, partNames, partPath]
        pprint.pprint(searchResults[1])
        return

def exploreTree():
    while True:
        inputChoices = ['Search for Part', 'Print Tree', 'Quit']
        userInput = pyip.inputMenu(inputChoices, numbered=True)
        if userInput == inputChoices[0]:
            searchPart(rootNode)
        if userInput == inputChoices[1]:
            rootNode.printTree()
        if userInput == inputChoices[2]:
            break

if __name__ == '__main__':

    rootNode = buildDataModel(importedBomFile)
    
    # exploreTree()
    # rootNode.printTree()

    # while True:
    #     print('Print Input: ', end='')
    #     userInput = pyip.inputStr()
    #     rootNode.printTree(userInput)