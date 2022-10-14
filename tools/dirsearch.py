from fnmatch import fnmatch
import os
from pprint import pprint
import re
from datetime import datetime

path = os.getcwd()
# # pattern = '*.bom[.]?[\d]?'
# pattern = r'*.bom.\d*'

bomFileRegex = re.compile(r'(\S+).bom.[\d]*')

results = []
for root, dirs, files in os.walk('c:/creo_bom_imports'):
    for name in files:
        if bomFileRegex.search(name):
            search = bomFileRegex.search(name)[1]
            results.append(search)


pprint(results)

