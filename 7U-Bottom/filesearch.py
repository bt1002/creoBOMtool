from pathlib import Path
import os, logging
import re
from unicodedata import name

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) # Get working directory of file
os.chdir(BASE_DIR)
CURDIR = Path(os.getcwd())

FILEPATH = Path('file_folder')
IMAGE_PATH = CURDIR / Path('images')


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

    lines = [['file1', 'prt'],['file2', 'prt'],['file1','asm']]

    # Search for image file
    for line in lines:
        fileName = searchFileImg(line[0], line[1], FILEPATH)
        print(fileName)



