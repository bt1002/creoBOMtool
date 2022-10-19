import logging
import os
import re
from datetime import datetime
from pathlib import Path

import pyinputplus as pyip

import lib.constants as c
from lib.bomexport import exportExcel, exportJSON
from lib.builddata import buildDataModel
from lib.creoClass import CreoNode, searchPart

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


if __name__ == "__main__":

    print(
        """\n--------------------------------------
    Welcome to Creo BOM Import/Export Tool"""
    )

    activeNode = None  # class CreoNode Node
    activeBOMnp = None
    activeBOMFile = None
    filenameprefix = ""
    filenamesuffix = ""

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
                exportJSON(activeNode, filenameprefix, filenamesuffix)
        else:
            print("Exiting Creo BOM Import/Export Tool")
            exit()
