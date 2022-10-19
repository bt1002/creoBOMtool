import logging
import re
from datetime import datetime
from pathlib import Path

import numpy as np

# import constants as c
# from creoClass import CreoNode
from . import constants
from .creoClass import CreoNode


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
    writeBomCheckFiles(
        unmergedBOMparts, mergedBOMparts, unmergedBOMasm, mergedBOMasm, np_bomSummary
    )

    writeBOM(fullMergedBOM)

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

    unmergedPartBomPath = constants.LOG_DIR / Path("unmergedPartBom.txt")
    with unmergedPartBomPath.open("w+", encoding="utf-8-sig") as fileObject:
        for i in unmergedBOMparts:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')

    mergedPartBomPath = constants.LOG_DIR / Path("mergedPartBom.txt")
    with mergedPartBomPath.open("w+", encoding="utf-8-sig") as fileObject:
        for i in mergedBOMparts:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')

    bomSummaryPath = constants.LOG_DIR / Path("bomSummary.txt")
    with bomSummaryPath.open("w+", encoding="utf-8-sig") as fileObject:
        for i in bomSummary:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')

    unmergedASmBOMPath = constants.LOG_DIR / Path("unmergedAsmBom.txt")
    with unmergedASmBOMPath.open("w+", encoding="utf-8-sig") as fileObject:
        for i in unmergedBOMasm:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')

    mergedASmBOMPath = constants.LOG_DIR / Path("mergedAsmBom.txt")
    with mergedASmBOMPath.open("w+", encoding="utf-8-sig") as fileObject:
        for i in mergedBOMasm:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')

    return None


def writeBOM(fullMergedBOM):

    # now = datetime.now()
    MERGED_BOM_EXP_PATH = constants.LOG_DIR / Path("FullyMergedBOM" + ".txt")
    with MERGED_BOM_EXP_PATH.open("w+", encoding="utf-8-sig") as fileObject:
        for i in fullMergedBOM:
            a = str(i[0])
            b = str(i[1])
            c = str(i[2])
            fileObject.write(f'{a.ljust(8," ")} {b.ljust(8," ")} {c}\n')


if __name__ == "__main__":
    print("Not intended to run standalone")
