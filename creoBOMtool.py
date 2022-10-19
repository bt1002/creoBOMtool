import logging
import os
import re
from datetime import datetime
from pathlib import Path

import anytree
import numpy as np
# import openpyxl
import pyinputplus as pyip
from anytree.exporter import JsonExporter

import lib.constants as c
from lib.creoClass import CreoNode
from lib.bomexcelexport import exportExcel

# Logging variables
try:
    os.remove(c.LOG_PATH)  # clears previous log file
except FileNotFoundError:
    print(f"Creating Logfile: {str(c.LOG_FILE)}")
logging.basicConfig(
    filename=str(c.LOG_PATH),
    level=logging.CRITICAL,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
# logging.disable()


def exploreTree(node):

    while True:
        print(f"\nActive Model: {activeAsmStr}\n")
        inputChoices = ["Search for Part", "Print Master Tree", "Return to Main Menu"]
        userInput = pyip.inputMenu(inputChoices, numbered=True)
        if userInput == inputChoices[0]:
            searchPart(node)
        if userInput == inputChoices[1]:
            node.printTree()
        if userInput == inputChoices[2]:
            break


def findBOMfile():
    bomRegex = re.compile(r".bom.[\d]*")

    results = []
    for root, dirs, files in os.walk(c.IMPORT_DIR):
        for name in files:
            if bomRegex.search(name):
                results.append(name)
    if results == []:
        return None
    else:
        return results


def searchPart(node):
    """Searches input node for parts with ID"""
    while True:

        searchResults = []

        userInput = pyip.inputStr('Enter Part Name (enter "quit" for quit):  ')
        if userInput.lower() == "quit":
            break
        else:
            creoParts = node.humanSearchTreeName(userInput)
            partNames = []
            partTypes = []
            partQtys = []
            partPath = []

            resultIndex = 1
            for part in creoParts:
                partNames.append(part.name)
                partTypes.append(part.type)
                partQtys.append(part.qty)
                partPath.append(part.getParentsPrintout())
                searchResults.append(part)
                # print(f'[{str(resultIndex).rjust(3," ")}] | {part.name.ljust(36,"_")} | {part.type} | TOTAL QTY: {str(part.totalTreeQTY).rjust(3,"*")} | {part.getParentsPrintout()}')
                print(
                    f'[{str(resultIndex).rjust(3," ")}] | {part.name.ljust(36,"_")} | {part.type} | BRANCH QTY {str(part.branchQTY).rjust(3,"*")} | {part.getParentsPrintout()}'
                )
                resultIndex += 1

        inputChoices = ["Print Tree for Item", "Search for Part", "Return to main"]
        userInput = pyip.inputMenu(inputChoices, numbered=True)
        if userInput == inputChoices[0]:
            partChoiceNum = pyip.inputInt("Enter part selection [#]: ")
            part = searchResults[partChoiceNum - 1]

            similarParts = node.findByName(
                searchterm=part.name, type=part.type, exact=True
            )

            print(f"\n{part.getParentsPrintout()}")
            part.printTree()
            print(f"\nName: {part.name}")
            print(f"Total ASM QTY: {part.totalTreeQTY}\n------\n")
            print("Locations Used:")
            for part in similarParts:
                print(part.getParentsPrintout())
            print("-----\n")

            break
        if userInput == inputChoices[1]:
            continue
        if userInput == inputChoices[2]:
            break


def buildDataModel(filePath):
    # Import BOM file and strip out blank lines

    now = datetime.now()
    bomRegex = re.compile(r"(\S+)(.bom.)[\d]*")
    filenameprefix = bomRegex.search(filePath.name)[1]  # type: ignore
    filenamesuffix = "_" + now.strftime("%y%d%m_%H%M")

    rows = []
    print(f"Importing file: {filePath}")
    with open(filePath, "r", encoding="utf-8-sig") as file_object:
        contents = file_object.readlines()
        for row in contents:  # Ignores simplfied rep not present warning at header
            if "WARNING: Some" in row:
                print(
                    """
                WARNING: Some components excluded from the active Simplified Rep. are currently not in session.
                This may produce inconsistencies in BOM output.'
                """
                )
            elif "not in session" in row:
                continue
            if row != "\n":
                row.strip()
                rows.append(row)

    # Establish root assembly item" row 1 and top level assembly
    print("Building Root Row...")
    rootRow = rows[0]
    rows.pop(0)
    rootRow = rootRow.strip().split()
    # rootID = f'{rootRow[1]}.{rootRow[0]}.0.0'

    rootNode = CreoNode(name=rootRow[1], type=rootRow[0], bomID=1, qty=1)
    rootNode.totalTreeQTY = 1
    logging.debug(f"Assembly Node Created: {rootRow[0]}, {rootRow[1]}")

    rIndex = 0
    cBOMID = 1
    for row in rows:
        row = row.strip().split()
        if row[0] == "Sub-Assembly":
            break
        logging.debug(f"Main assembly item routine started: {row[2]}, QTY {row[0]}")
        cQTY, cType, cName = row[0:3]
        CreoNode(cName, cType, cBOMID, cQTY, parent=rootNode)
        cBOMID += 1
        rIndex += 1
    rows = rows[rIndex:]

    cSubAsmNode = None
    noParentNode = CreoNode(
        name="NOPARENTNODE", type="CONTAINER", bomID=1, qty=1, parent=None
    )

    # Iterate file rows looking for Assemblies or Parts and create 'Nodes'
    print("Parsing BOM...")
    summaryRowStart = 0
    sumRowIndex = 0
    for row in rows:
        row = row.strip().split()
        sumRowIndex += 1
        # If read row starts with part summary line, exit loop
        if row[0] == "Summary":
            logging.info(
                f"Summary of Parts found...row: {sumRowIndex}\n---EXITING LOOP---"
            )
            summaryRowStart = sumRowIndex + 1
            break

        # Handles an error with bom export including line about "Model not included in current Configuration State"
        elif row[0:3] == ["Model", "not", "included"]:
            logging.info(f"Model not included in current Configuration State for {cSubAsmNode.name}, ignored")  # type: ignore
            continue

        # If read row is an assembly, iterate from bottom of tree upwards looking for a part name match in higher level parent
        # First part name found in upper level will be assigned as the new parent item and add following items as children
        elif row[0] == "Sub-Assembly":
            subAssyName = row[1]
            cBOMID = 1
            cSubAsmNode = CreoNode(
                name=subAssyName, type="ASM", bomID=0, qty=10, parent=noParentNode
            )
            logging.debug(f"Sub-Assembly Header Identified: {row[0]}, {row[1]}")
            continue

        # If read row is a sub-bom item, create node of parts and assign parent and part properties
        else:
            cQTY, cType, cName = row[0:3]
            cNode = CreoNode(cName, cType, cBOMID, cQTY, parent=cSubAsmNode)
            logging.debug(f"Parent name {cNode.parent.name}, child name {cNode.name}")  # type: ignore
            cBOMID += 1

    # Checks for intentionally empty assemblies in tree (no parts)
    logging.info("Finding assemblies with no parts...")
    noParentNode.fix_empty_asm()

    # Subroutine that iterates indefinately across ophaned sub-assemblies and adds them as BOM items
    logging.info("Creating children for sub-assemblies in root...")
    rootNode.create_node_children(noParentNode)

    # Output list of summary from BOM import
    logging.info(f"Starting Part Summary")
    summaryRows = rows[summaryRowStart - 1 :]
    bomSummaryQTY = []
    bomSummaryType = []
    bomSummaryName = []
    for row in summaryRows:
        row = row.strip().split()
        bomSummaryQTY.append(int(row[0]))
        bomSummaryType.append(row[1])
        bomSummaryName.append(row[2])
    bomSummary = [bomSummaryQTY, bomSummaryType, bomSummaryName]

    np_bomSummary = np.array(bomSummary)
    np_bomSummary = np_bomSummary.transpose()
    np_bomSummary = np_bomSummary[np_bomSummary[:, 2].argsort()]

    # Create array of all unique parts
    logging.info(f"Calculating BOM")
    allParts = rootNode.findParts()

    # Set extended quantities for each branch
    for part in allParts:  # type: ignore
        part.setBranchQTY()

    mergedBOMparts, unmergedBOMparts = mergeBOM(allParts)

    # Create array of all unique assembles
    allAsm = rootNode.findAsm()
    for asm in allAsm:  # type: ignore
        asm.setBranchQTY()

    mergedBOMasm, unmergedBOMasm = mergeBOM(allAsm)

    fullMergedBOM = np.append(mergedBOMparts, mergedBOMasm, axis=0)

    # Set total assembly quantities to match to node type, NOTE: this is not dynamic if tree is changed
    for line in fullMergedBOM:
        lineQTY = line[0]
        if line[1] == "Part":
            lineType = "PRT"
        else:
            lineType = "ASM"

        lineName = line[2]
        nodeMatches = rootNode.findByName(
            type=lineType, searchterm=lineName, exact=True
        )
        for creoNode in nodeMatches:  # type: ignore
            creoNode.totalTreeQTY = lineQTY

    ### Write unmerged, merged, and bom summary to file for manual check ###
    # writeBomCheckFiles(unmergedBOMparts, mergedBOMparts, unmergedBOMasm, mergedBOMasm, np_bomSummary)

    #### Write full asm BOM ####
    try:
        comparison = mergedBOMparts == np_bomSummary
        equal_arrays = comparison.all()
        print(f"Completed BOM check: {equal_arrays}")

    except:
        print(
            """---- WARNING ----
        
        BOM check failed:
        Potential issues include corrupted BOM or simplified rep without entire tree shown
        Check manual exports to verify, assembly tree with be used as source of data NOT creo BOM part rollup
        
        -----"""
        )

    print("Completed tree build.")
    return rootNode, fullMergedBOM


def mergeBOM(creoAsm):
    #### Following section is used to check if BOM is built with the correct quantities after the tree is constructed.
    #### It checks against the creo exported part count list
    # Create unmerged BOM tree list for branch quantities
    partQTY = []
    partType = []
    partName = []
    for part in creoAsm:
        partQTY.append(part.branchQTY)
        if part.type[0].lower() in "p":
            partType.append("Part")
        else:
            partType.append(part.type)
        partName.append(part.name)
    unmergedBOM = [partQTY, partType, partName]

    np_unmergedBOM = np.array(unmergedBOM)
    np_unmergedBOM = np_unmergedBOM.transpose()
    np_unmergedBOM = np_unmergedBOM[np_unmergedBOM[:, 2].argsort()]

    # Create merged list of BOM items with full tree quantities for each unique part
    mergedQTY = []
    mergedType = []
    mergedName = []
    for i in range(len(creoAsm)):
        if unmergedBOM[2][i] not in mergedName:  # If partname not in merged bom
            mergedQTY.append(unmergedBOM[0][i])
            mergedType.append(unmergedBOM[1][i])
            mergedName.append(unmergedBOM[2][i])
        else:
            for j in range(len(mergedName)):
                if unmergedBOM[2][i] == mergedName[j]:
                    temp = mergedQTY[j]
                    mergedQTY[j] = mergedQTY[j] + unmergedBOM[0][i]
    mergedBOM_parts = [mergedQTY, mergedType, mergedName]

    np_mergedBOM_parts = np.array(mergedBOM_parts)
    np_mergedBOM_parts = np_mergedBOM_parts.transpose()
    np_mergedBOM_parts = np_mergedBOM_parts[np_mergedBOM_parts[:, 2].argsort()]

    return np_mergedBOM_parts, np_unmergedBOM


def writeBomCheckFiles(
    unmergedBOMparts, mergedBOMparts, unmergedBOMasm, mergedBOMasm, bomSummary
):

    """Write unmerged, merged, and bom summary to file for manual check
    requires 3 file np array types with following column data: qty, type, name"""

    unmergedPartBomPath = c.LOG_DIR / Path("unmergedPartBom.txt")
    with unmergedPartBomPath.open(encoding="utf-8-sig") as fileObject:
        for i in unmergedBOMparts:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')

    mergedPartBomPath = c.LOG_DIR / Path("mergedPartBom.txt")
    with mergedPartBomPath.open("w", encoding="utf-8-sig") as fileObject:
        for i in mergedBOMparts:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')

    bomSummaryPath = c.LOG_DIR / Path("bomSummary.txt")
    with bomSummaryPath.open("w", encoding="utf-8-sig") as fileObject:
        for i in bomSummary:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')

    unmergedASmBOMPath = c.LOG_DIR / Path("unmergedAsmBom.txt")
    with unmergedASmBOMPath.open("w", encoding="utf-8-sig") as fileObject:
        for i in unmergedBOMasm:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')

    mergedASmBOMPath = c.LOG_DIR / Path("mergedAsmBom.txt")
    with mergedASmBOMPath.open("w", encoding="utf-8-sig") as fileObject:
        for i in mergedBOMasm:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')


    return None


def writeBOM(fullMergedBOM):

    # now = datetime.now()
    MERGED_BOM_EXP_PATH = c.MERGED_BOM_EXP_DIR / Path(filenameprefix + "BOM" + ".txt")
    with MERGED_BOM_EXP_PATH.open("w", encoding="utf-8-sig") as fileObject:
        for i in fullMergedBOM:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')


def exportJSON(activeNode):
    # Data and file export to JSON
    exporter = JsonExporter(indent=2, sort_keys=True)
    JSON_EXP_PATH = c.JSON_EXP_DIR / Path(filenameprefix + filenamesuffix + ".JSON")
    logging.info(f"Writing JSON to file {str(JSON_EXP_PATH)}")
    print(f"Writing JSON to file {str(JSON_EXP_PATH)}")
    with JSON_EXP_PATH.open("w", encoding="utf-8-sig") as fileObject:
        fileObject.write(exporter.export(activeNode))


if __name__ == "__main__":

    print(
        """\n--------------------------------------
    Welcome to Creo BOM Import/Export Tool"""
    )

    activeNode = None  # class CreoNode Node
    activeBOMnp = None
    activeBOMFile = None
    filenameprefix = ''
    filenamesuffix = ''

    while True:
        if isinstance(activeNode, CreoNode) == False:
            activeAsmStr = "None"
        else:
            activeAsmStr = activeNode.name  # type: ignore

        mainMenuChoices = [
            "Import BOM",
            "Explore BOM",
            "Export to Excel",
            "Export to JSON",
            "Quit",
        ]
        print(f"\nActive Model: {activeAsmStr}\n")
        userinput = pyip.inputMenu(mainMenuChoices, numbered=True)

        if userinput == mainMenuChoices[0]:  # Import BOM TXT File
            print("BOM Files Found:")
            bomFiles = findBOMfile()
            if bomFiles == None:
                print("No BOM files found.")
                break
            if len(bomFiles) == 1:
                activeBOMtxt = bomFiles[0]
            else:
                activeBOMtxt = pyip.inputMenu(bomFiles, numbered=True)
            activeNode, activeBOMnp = buildDataModel(c.IMPORT_DIR / Path(activeBOMtxt))
            now = datetime.now()
            bomFileRegex = re.compile(r"(\S+)(.bom.)[\d]*")
            filenameprefix = bomFileRegex.search(activeBOMtxt)[1]  # type: ignore
            filenamesuffix = "_" + now.strftime("%y%d%m_%H%M")

        elif userinput == mainMenuChoices[1]:  # Explore BOM
            if isinstance(activeNode, CreoNode) == False:
                print("No active assembly set.")
            else:
                exploreTree(activeNode)

        elif userinput == mainMenuChoices[2]:  # Export to Excel
            if isinstance(activeNode, CreoNode) == False:
                print("No active assembly set.")
            else:
                exportExcel(activeNode, activeBOMnp, filenameprefix, filenamesuffix)

        elif userinput == mainMenuChoices[3]:  # Export to JSON
            if isinstance(activeNode, CreoNode) == False:
                print("No active assembly set.")
            else:
                exportJSON(activeNode)
        else:
            print("Exiting Creo BOM Import/Export Tool")
            exit()
