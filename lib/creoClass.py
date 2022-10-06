# Define part classes
from distutils.command.build import build
from anytree import AnyNode, RenderTree

class CreoAsm(AnyNode):
    '''Inhereted class from AnyNode, creates Tree node with QTY'''
    def __init__(self, name, type, bomID, qty, level=None, parent=None, children=None, **kwargs):
        super().__init__(parent, children, **kwargs)
        self.name = name
        self.type = type
        self.level = level
        self.bomID = bomID
        self.qty = qty
        self.unID = f'{name}.{type}.{level}.{bomID}'
    
    def printTree(self):
        print(RenderTree(self))