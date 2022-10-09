# Define part classes
from distutils.log import debug
from anytree import AnyNode, NodeMixin, SymlinkNodeMixin, RenderTree, PreOrderIter, PostOrderIter, findall, search
import re, logging, anytree
from copy import copy, deepcopy

class CreoFile():
    '''Creo Part'''
    def __init__(self, name, type, bomID, qty):
        self.name = name
        self.bomID = bomID
        self.qty = int(qty)
        if type[0] == "S" or type[0] == "A":
            self.type = 'ASM'
        elif type == "Part":
            self.type = 'PRT'
        else:
            self.type = type


class CreoNode(NodeMixin, CreoFile):
    '''Creates Tree Node of a CreoAsm part class'''
    def __init__(self, name, type, bomID, qty, parent=None, children=None, **kwargs):
        super().__init__(name, type, bomID, qty)
        self.branchQTY = 0
        self.printID = f'{name.ljust(40,"_")}| QTY: {str(self.qty).rjust(3,"*")} | {self.type} | BOMID: {str(self.bomID).rjust(3,"*")}'
        self.parent = parent
        if children:
            self.children = children

    def printTree(self, level=None) -> "CreoNode":
        '''Prints tree of Node'''
        if level == None:
            print(RenderTree(self).by_attr('printID'))
        else:
            print(RenderTree(self, maxlevel=level+1).by_attr('printID'))
    
    def getParentsPrintout(self) -> "CreoNode":
        '''Returns string of parent path'''
        parentNames = []
        for node in self.iter_path_reverse():
            parentNames.append(node.name)
        return ' -> '.join(parentNames)

    def getParents(self) -> "CreoNode":
        '''Returns string of parent path'''
        return self.ancestors
    
    def searchTreeName(self, partName) -> "CreoNode":
        '''Searches tree for all nodes by str value'''
        if type(partName) != type('string'):
            return            
        partName = partName.lower()
        partList = self.findByName(partName, exact=False)
        strNames = []
        for node in partList:
            strNames.append({'name':node.name, 'path': node.getParentsPrintout})
        return partList
    
    def findByName(self, searchterm='', exact=False):
        '''Search part tree for all unique nodes'''
        if exact:
            partList = findall(self, filter_=lambda node: searchterm.lower() == node.name.lower() )
            return partList
        else:
            partList = findall(self, filter_=lambda node: searchterm.lower() in node.name.lower() )
            return partList

    def searchLeaves(self) -> "CreoNode":
        '''Searches part tree for all leaves (no children)'''
        leaves = []
        for CreoNode in self.descendants:  # walk down from the root
            if CreoNode.is_leaf:
                leaves.append(CreoNode)
        return leaves

    def setBranchQTY(self) -> "CreoNode":
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

    def __copy__(self) -> "CreoNode":
        """Computes a deep copy of the sub-tree the node is a root of"""
        return self.__class__(
            self.name, self.type, self.bomID, self.qty
    )

    def __deepcopy__(self, memodict={}) -> "CreoNode":
        """Computes a deep copy of the sub-tree the node is a root of

        ATTENTION: this copy mechanism does only copy the instances from `self` downwards!
        -> call deepcopy(root_node) to copy a full tree
        """
        # my_copy = self.__nodeCopy__()
        my_copy = copy(self)
        # recursion towards the leaves
        my_copy.children = [deepcopy(child) for child in self.children]
        return my_copy

    # def copy_creo_node_tree(self) -> "CreoNode": ###########BUGGED###########
    #     """computes a deep copy of the full tree the node belongs to

    #     Returns: the node corresponding to `self` in the copied tree
    #     """
    #     my_root = self.root
    #     my_root_copy = deepcopy(my_root)  # full copy of my tree
    #     # find copy of myself based on matching the some argument along the path
    #     # NOTE: more efficient than searching the whole tree
    #     matched_node = my_root_copy
    #     for node in self.path:  # walk down from the root
    #         if (
    #             node.is_root
    #         ):  # skip the first node in the path = root, has been matched already
    #             continue
    #         label2match = node.name
    #         # matched_node = anytree.search.find(
    #         #     matched_node, lambda n: n.name == label2match
    #         # )
            
    #         matched_node = node.findByName(label2match, True)[0] # returns first item in tuple which must be a match
    #     my_copy = matched_node
    #     return my_copy

    def find_missing_children(self) -> "CreoNode":
        missingChildren = []
        for CreoNode in self.descendants:  # walk down from the root
            if (CreoNode.type[0] == 'P'):  # Ignore parts
                continue
            if CreoNode.is_leaf:
                missingChildren.append(CreoNode)
        for child in missingChildren:
            print(f'Missing child: {child.type} | {child.name}')
            print(f'{child.children}')
        return missingChildren

    def assign_children(self, creoNodeCopy) -> "CreoNode":
        '''Reassigns children of one node to another node'''
        self.children = creoNodeCopy.children

    def fix_missing_children(self):
        missing_children = self.find_missing_children()
        for nodeMissing in missing_children:
            matchingParts = self.findByName(nodeMissing.name, True)
            for nodeMatch in matchingParts: # Search for node that has sub-nodes to copy
                if nodeMatch.is_leaf == False: 
                    # print(f"nodeMatch.is_leaf =  {nodeMatch.is_leaf}")
                    # print(f'nodematch = {nodeMatch.name}')
                    nodeWithParts = nodeMatch.__deepcopy__()



                    # print(nodeWithParts.getParentsPrintout())

                    nodeWithParts.parent = None # sever link to tree
                    nodeMissing.assign_children(nodeWithParts) # reassign children to missing nodes

                    break

    
        


    # find copy of node with same name in root tree, create copy
    # create copy of node from exiting tree with children
    # assign child copies to new node
