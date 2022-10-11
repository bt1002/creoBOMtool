from pathlib import Path
import os, logging
import re

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) # Get working directory of file
os.chdir(BASE_DIR)


# Search for image file
print(dirFiles)
regexImage = re.compile(r'(^\w+)(PRT|ASM|prt|asm)().(jpg|png|JPG|PNG)')

dirFiles = []
for file in os.listdir('./images/'):
    if file.endswith('jpg')






# print(output)