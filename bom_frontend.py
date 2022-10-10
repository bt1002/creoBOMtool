from lib.creoClass import CreoNode
from pathlib import Path
from anytree import AnyNode
from anytree import RenderTree
import pickle
import os, logging, pprint
import pyinputplus as pyip

# treeJSON = 'chassis-000.bom.json'
# treeBinary = './7U-Bottom/7u-bottom.bom.1.pk'
treeBinary = './BOM_imports/chassis-000.bom.pk'

# logpath = './7U-Bottom/logs/'
# logname = 'bom_frontend.txt'

# try:
#     os.remove(logpath + logname) # clears previous log file
#     print('Clearing Logfile')
# except:
#     print(f'Creating Logfile: {logpath}{logname}')
# logging.basicConfig(filename=logpath+logname, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.disable()

# Declare basepath and filenames
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) # Get working directory of file
os.chdir(BASE_DIR)

def importPickleBinary():

    with open(treeBinary, 'rb') as input:
        creoNode = pickle.load(input)
    return creoNode

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
