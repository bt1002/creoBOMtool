# Define part classes
from anytree import AnyNode, RenderTree

class CreoAsm(AnyNode):
    '''Inhereted class from AnyNode, creates Tree node with QTY'''
    def __init__(self, parent=None, children=None, qty=0 **kwargs):
        super().__init__(parent, children, **kwargs)
        self.qty=qty
    
    def printTree(self):
        print(RenderTree(self))