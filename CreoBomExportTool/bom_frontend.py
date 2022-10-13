from pathlib import Path
import os, logging, pickle
import pyinputplus as pyip

# Declare basepath and filenames
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) # Get working directory of file
os.chdir(BASE_DIR)

# Filename declarations
LOG_FILE = Path('bom_frontend.py.txt')
MERGED_BOM_FILE = Path('MERGED_BOM_FILE.txt')
BINARY_IMP_FILE = Path('BINARY_EXPORT.pk')

# Get current working directory
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) # Get working directory of file
os.chdir(BASE_DIR)

# Folder locations for data
LOG_ROOT_PATH = Path('./logs')
EXPORT_ROOT_PATH = Path('./exports')

# Export locations
LOG_PATH = LOG_ROOT_PATH / LOG_FILE
MERGED_BOM_EXP_PATH = EXPORT_ROOT_PATH / MERGED_BOM_FILE
BINARY_IMP_PATH = EXPORT_ROOT_PATH / BINARY_IMP_FILE

# Logging variables
try:
    os.remove(LOG_PATH) # clears previous log file
except:
    print(f'Creating Logfile: {LOG_FILE}')
logging.basicConfig(filename=LOG_PATH, level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.disable()

def importPickleBinary():

    with BINARY_IMP_PATH.open('rb') as input:
        rootNode, fullMergedBOM = pickle.load(input)
    return rootNode

def exploreTree(node):

    while True:
        inputChoices = ['Search for Part', 'Print Master Tree', 'Quit']
        userInput = pyip.inputMenu(inputChoices, numbered=True)
        if userInput == inputChoices[0]:
            searchPart(node)
        if userInput == inputChoices[1]:
            node.printTree()
        if userInput == inputChoices[2]:
            break

def searchPart(node):
    '''Searches input node for parts with ID'''
    while True:

        searchResults = []

        userInput = pyip.inputStr('Enter Part Name (enter "quit" for quit):  ')
        if userInput.lower() == 'quit':
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
                print(f'[{str(resultIndex).rjust(3," ")}] | {part.name.ljust(36,"_")} | {part.type} | BRANCH QTY {str(part.branchQTY).rjust(3,"*")} | {part.getParentsPrintout()}')
                resultIndex += 1
            
        inputChoices = ['Print Tree for Item', 'Search for Part', 'Return to main']
        userInput = pyip.inputMenu(inputChoices, numbered=True)
        if userInput == inputChoices[0]:
            partChoiceNum = pyip.inputInt('Enter part selection [#]: ')
            part = searchResults[partChoiceNum-1]
            
            similarParts = node.findByName(searchterm=part.name, type=part.type, exact=True)
            
            print(f'\n{part.getParentsPrintout()}')
            part.printTree()
            print(f'\nName: {part.name}')
            print(f'Total ASM QTY: {part.totalTreeQTY}\n------\n')
            print(f'Locations Used:')
            for part in similarParts:
                print(part.getParentsPrintout())
            print('-----\n')

            break
        if userInput == inputChoices[1]:
            continue
        if userInput == inputChoices[2]:
            break

if __name__ == '__main__':

    asmNode = importPickleBinary()
    exploreTree(asmNode)
