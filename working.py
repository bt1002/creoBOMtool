from lib.creoClass import CreoAsm
from pathlib import Path
import os, logging, pprint
import pyinputplus as pyip
from anytree import Node, RenderTree, AsciiStyle, PreOrderIter, PostOrderIter

f = Node("f")
b = Node("b", parent=f)
a = Node("a", parent=b)
d = Node("d", parent=b)
c = Node("c", parent=d)
e = Node("e", parent=d)
g = Node("g", parent=f)
i = Node("i", parent=g)
h = Node("h", parent=i)

# print(RenderTree(root))

# print(root.children)

# for child in root.children:
#     print(child.id)

# root.printTree()

# root.printParents()

targetNode = c

# parentNames = [node.name for node in PreOrderIter(c, maxlevel=c.depth)]
# print(f'{node.name} Depth {node.depth}')

parentNames = []
for node in targetNode.iter_path_reverse():
    parentNames.append(node.name)
print(' -> '.join(parentNames))
