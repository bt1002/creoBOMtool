import pprint
import numpy as np

leafQTY = [1,2,3,4,5]
leafType = ['P','P','P','P','P']
leafName = ["A", "B", "C", "A", "D"]

unmergedBOM = [leafQTY, leafType, leafName]

pprint.pprint(unmergedBOM)

mergedQTY = []
mergedType = []
mergedName = []

for i in range(len(leafName)):
    if unmergedBOM[2][i] not in mergedName:  # If partname not in merged bom
        mergedQTY.append(unmergedBOM[0][i])
        mergedType.append(unmergedBOM[1][i])
        mergedName.append(unmergedBOM[2][i])
    else:
        for j in range(len(mergedName)):
            if unmergedBOM[2][i] == mergedName[j]:
                mergedQTY[j] = mergedQTY[j] + unmergedBOM[0][i]
                # print(f'unmergedBOM[2][i] {unmergedBOM[2][i]}')
                # print(f'mergedName[j] {mergedName[j]}')
                # print(f'unmergedBOM[0][i] {unmergedBOM[0][i]}')
                break

mergedBOM = [mergedQTY, mergedType, mergedName]
pprint.pprint(mergedBOM)

