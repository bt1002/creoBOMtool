import openpyxl, pickle, re
from pathlib import Path
import os, anytree, logging
# import pyinputplus as pyip
# from lib.creoClass import CreoNode

# treeBinary = './BOM_imports/chassis-000.bom.pk'
treeBinary = './Excel/7u-bottom.bom.1.pk'

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) # Get working directory of file
os.chdir(BASE_DIR)

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

# if __name__ == '__main__':

asmNode = importPickleBinary()

# Expand tree in order from top to bottom as line items
treeDepth = asmNode.height

# # Create workbook class
wrkb = openpyxl.Workbook()
# # Number of sheets in the workbook (1 sheet in our case)
ws = wrkb.worksheets[0]

## Print Rows:
"""
- Name
- Image (skip)
- QTY
- FULLQTY
- LEVELS(1-N:(max depth))
"""
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

    # Search for image file
    dirFiles = os.listdir('.\images\')
    regexImage = re.compile(r'(^\w+)(PRT|ASM|prt|asm)().(jpg|png|JPG|PNG)')
    dirFiles.search(dirFiles)

# Resize for image import
ws.column_dimensions['A'].width = 40
ws.column_dimensions['B'].width = 20

for row in range(ws.max_row+1):
    if row == 0:
        ws.row_dimensions[row].height = 20
    else:
        ws.row_dimensions[row].height = 100


img = openpyxl.drawing.image.Image('./Excel/bushingprt.JPG')
img.anchor = 'B2'
ws.add_image(img)

wrkb.save('out_test.xlsx')




# Find image for each name
"""
find by name, associate to row #
"""

# Embed image in column 2
"""
Resize column B width
Resize rows with items
embed image into column B, row n
"""



