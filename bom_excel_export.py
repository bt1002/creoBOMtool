import openpyxl, pickle, re
from pathlib import Path
import os, anytree, logging
# import pyinputplus as pyip
# from lib.creoClass import CreoNode

# treeBinary = './BOM_imports/chassis-000.bom.pk'
treeBinary = './Excel/7u-bottom.bom.1.pk'

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) # Get working directory of file
os.chdir(BASE_DIR)

IMAGE_DIR = Path('7U-Bottom/images')

# logpath = './7U-Bottom/logs/'
# logname = 'bom_frontend.txt'

# try:
#     os.remove(logpath + logname) # clears previous log file
#     print('Clearing Logfile')
# except:
#     print(f'Creating Logfile: {logpath}{logname}')
# logging.basicConfig(filename=logpath+logname, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.disable()

def importPickleBinary():

    with open(treeBinary, 'rb') as input:
        creoNode = pickle.load(input)
    return creoNode

def searchFileImg(partName, partType, directory):
    '''Searches "directory" for image file using part name and type'''

    print(directory)
    imageNameFiles = os.listdir(directory)

    regexImage = re.compile((f'{str(partName)}') + r'(prt|asm).(jpg|png|jpeg|)', re.IGNORECASE)
    for file in imageNameFiles:
        result = regexImage.match(file)
        if result:
            filePartType = result[1]
            if filePartType.lower() == partType.lower():
                print(f'Found math for {partName}.{partType} = {result[0]}')
                return result[0]
        else:
            return None

if __name__ == '__main__':

    asmNode = importPickleBinary()

    # Expand tree in order from top to bottom as line items
    treeDepth = asmNode.height
    wrkb = openpyxl.Workbook()     # # Create workbook class
    ws = wrkb.worksheets[0] # Number of sheets in the workbook (1 sheet in our case)

    # Print Rows: Name / Image / QTY / FULLQTY / LEVELS(1-N:(max depth))
    asmColumns = (treeDepth + 1) * ['']
    rowCount = 0

    # Print Header
    headerCol = asmColumns[:]
    for col in range(len(headerCol)): headerCol[col] = col + 1
    cell = ws['B2']
    header = ['Name', 'Image', 'QTY', 'TOTAL\nQTY'] + headerCol
    ws.append(header)
    ws.freeze_panes = cell

    # Print data to worksheet
    rowIndex = 1
    for node in anytree.PreOrderIter(asmNode):
        
        # Print Data
        rowAsmColumns = asmColumns
        col_name = node.name + '.' + node.type
        col_image = ''
        col_qty = node.qty
        col_fullQty = node.totalTreeQTY
        rowAsmColumns = asmColumns[:]
        rowAsmColumns[node.depth] = 'X'
        row = [col_name, col_image, col_qty, col_fullQty, node.depth] + rowAsmColumns
        ws.append(row)

        # Add file image
        imgName = searchFileImg(node.name, node.type, IMAGE_DIR)
        print(f'{node.name}, {node.type}')
        if imgName != None:
            img = openpyxl.drawing.image.Image(IMAGE_DIR / imgName)
            img.anchor = 'B' + str(rowIndex)
            ws.add_image(img)
        else:
            print(f'No image found for {node.name}.{node.type}')
            continue
        
        rowIndex += 1


    # Resize for image import
    ws.column_dimensions['A'].width = 40
    ws.column_dimensions['B'].width = 20

    for row in range(ws.max_row+1):
        if row == 0:
            ws.row_dimensions[row].height = 20
        else:
            ws.row_dimensions[row].height = 100

    wrkb.save('out_test.xlsx')

