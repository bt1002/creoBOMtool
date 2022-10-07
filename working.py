from lib.creoClass import CreoAsm
from pathlib import Path
import os, logging, pprint
import pyinputplus as pyip
from anytree import Node, RenderTree, AsciiStyle, PreOrderIter, PostOrderIter, findall_by_attr
from anytree import Node, RenderTree, AsciiStyle, Walker

type = "P"
bom = 1
qty = 1

f = CreoAsm("f", type, bom, qty, )
b = CreoAsm("b", type, bom, qty, parent=f)
ab = CreoAsm("ab", type, bom, qty, parent=b)
d = CreoAsm("d", type, bom, qty, parent=b)
c = CreoAsm("c", type, bom, qty, parent=d)
e = CreoAsm("e", type, bom, qty, parent=d)
x = CreoAsm("x", type, bom, qty, parent=f)
i = CreoAsm("i", type, bom, qty, parent=x)
hx = CreoAsm("hx", type, bom, qty, parent=i)

# print(RenderTree(root))

# print(root.children)

# for child in root.children:
#     print(child.id)

targetNode = f

# parentNames = [node.name for node in PreOrderIter(c, maxlevel=c.depth)]
# print(f'{node.name} Depth {node.depth}')

targetNode.printTree()
# print(targetNode.getParents())

# userInput = pyip.inputStr('Enter Part Name')
# creoParts = f.searchTree(userInput)
# pprint.pprint(creoParts)
# partNames = []
# partPath = []
# for part in creoParts:
#     partNames.append(part.name)
#     partPath.append(part.getParents())
# print(partNames)

# allNodes = f.allNodes()
# pprint.pprint(allNodes)
# type = type(allNodes[0])
# pprint.pprint(type)

parts = targetNode.searchLeaves()
pprint.pprint(parts)
