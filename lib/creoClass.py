# Define part classes
from anytree import AnyNode, RenderTree, PreOrderIter, PostOrderIter, findall
import re

class CreoAsm(AnyNode):
    '''Inhereted class from AnyNode, creates Tree node with QTY'''
    def __init__(self, name, type, bomID, qty, parent=None, children=None, **kwargs):
        super().__init__(parent, children, **kwargs)
        self.name = name
        self.bomID = bomID
        self.qty = int(qty)
        self.branchQTY = 0
        if type == "Sub-Assembly" or type == "Assembly":
            self.type = 'A'
        elif type == "Part":
            self.type = 'Part'
        else:
            self.type = type
        self.printID = f'{name.ljust(40,"_")}| QTY: {str(self.qty).rjust(3,"*")} | {self.type} | BOMID: {str(self.bomID).rjust(3,"*")}'

    def printTree(self, level=None):
        '''Prints tree of Node'''
        if level == None:
            print(RenderTree(self).by_attr('printID'))
        else:
            print(RenderTree(self, maxlevel=level+1).by_attr('printID'))
    
    def printParents(self):
        '''Returns string of parent path'''
        parentNames = []
        for node in self.iter_path_reverse():
            parentNames.append(node.name)
        return ' -> '.join(parentNames)

    def getParents(self):
        '''Returns string of parent path'''
        return self.ancestors
    
    def searchTree(self, partName):
        '''Searches tree for all nodes by str value'''
        if type(partName) != type('string'):
            return            
        partName = partName.lower()
        partList = findall(self, filter_=lambda node: (f'{partName}') in node.name.lower() )
        strNames = []
        for node in partList:
            strNames.append(node.name)
        return partList
    
    def searchNodes(self):
        '''Search part tree for all unique nodes'''
        partList = findall(self, filter_=lambda node: ('') in node.name.lower() )
        return partList

    def searchLeaves(self):
        '''Searches part tree for all leaves (no children)'''
        nodes = self.searchNodes()
        leaves = []
        for item in nodes:
            if item.is_leaf:
                leaves.append(item)
        return leaves

    def setBranchQTY(self):
        '''This will set branch multiplier to total qty in this leaf for parents qty > 1
        Unique value to each leaf'''
        parents = self.getParents()
        qtyMultiplier = 1

        #### DEBUG block to fix qty rollup
        # debug_name = 'YSF-54438-ZI'
        # if self.name == debug_name:
        #     print(f'debug QTY {self.qty}')
        #     for parent in parents:
        #         print(f'"{parent.name} x{parent.qty}')
        #         qtyMultiplier = parent.qty * qtyMultiplier
        #     self.branchQTY = self.qty * qtyMultiplier
        # else:
        
        for parent in parents:
            qtyMultiplier = parent.qty * qtyMultiplier
        self.branchQTY = self.qty * qtyMultiplier
        return self.branchQTY

