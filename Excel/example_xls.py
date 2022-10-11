import pprint
import numpy as np
import copy
import openpyxl

# It is not required for one to create a workbook on
# filesystem, therefore creating a virtual workbook
wrkb = openpyxl.Workbook()

# Number of sheets in the workbook (1 sheet in our case)
ws = wrkb.worksheets[0]

# Adding a row of data to the worksheet (used to
# distinguish previous excel data from the image)
ws.append([10,'','',2010, "Geeks", 4, "life"])

# A wrapper over PIL.Image, used to provide image
# inclusion properties to openpyxl library
img = openpyxl.drawing.image.Image('test.png')

# The Coordinates where the image would be pasted
# (an image could span several rows and columns
# depending on it's size)
img.anchor = 'A2'

# Adding the image to the worksheet
# (with attributes like position)
ws.add_image(img)

# Saving the workbook created under the name of out.xlsx
wrkb.save('out.xlsx')

