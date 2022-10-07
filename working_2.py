import pprint

unmergedBOM = [
  {"name": "Tom", "qty": 10, "type": 'p'},
  {"name": "Mark", "qty": 5, "type": 'p'},
  {"name": "Pam", "qty": 7, "type": 'p'},
  {"name": "Tom", "qty": 2, "type": 'p'}
]

mergedBOM = []
mergedBOMPartNames = []

for part in mergedBOMPartNames:
    partName = part["name"]
    if part["name"] == list(filter):
        mergedBOM.append(part)
    else:
        existingPart = next(item for item in mergedBOM if item["name"] == "Tom")
        print(f'Existing: {existingPart}')


pprint.pprint(mergedBOM)