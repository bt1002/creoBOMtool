# Define part classes
from anytree import AnyNode, RenderTree, PreOrderIter, PostOrderIter

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
    
    def printTree(self, level=None):
        if level == None:
            print(RenderTree(self,).by_attr())
        else:
            print(RenderTree(self, maxlevel=level).by_attr('unID'))
    
    def getParents(self):
        parentNames = []
        for node in self.iter_path_reverse():
            parentNames.append(node.name)
        return ' -> '.join(parentNames)
