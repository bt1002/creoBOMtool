# Define part classes
from unicodedata import name
from anytree import AnyNode, NodeMixin, SymlinkNodeMixin, RenderTree, PreOrderIter, PostOrderIter, findall, search
import re, logging, anytree
from copy import copy, deepcopy

class CreoFile():
    '''Creo Part'''
    def __init__(self, name, type, bomID, qty):
        if type[0] == "S" or type[0] == "A":
            self.type = 'ASM'
            self.empty = False # Default flag for assemblies, this needs to be handled
        elif type == "Part":
            self.type = 'PRT'
            self.empty = True
        elif type[0].lower() == "C".lower():
            self.type = "CONT"
        else:
            self.type = type
        self.name = name # + '.' + self.type
        self.bomID = bomID
        self.qty = int(qty)


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
        parentNames[0] = f'{self.name}.{self.type}'
        return ' -> '.join(parentNames)

    def getParents(self) -> "CreoNode":
        '''Returns string of parent path'''
        return self.ancestors
    
    def searchTreeName(self, partName, type='') -> "CreoNode":
        '''Searches tree for all nodes by str value'''
        partName = partName.lower()
        # partType = self.type
        partList = self.findByName(type, partName, exact=False)
        strNames = []
        for node in partList:
            strNames.append({'name':node.name, 'type':node.type, 'path': node.getParentsPrintout})
        return partList
    
    def findByName(self, type='', searchterm='', exact=False) -> "CreoNode":
        '''Search part tree for all unique nodes'''
        if exact:
            partList = findall(self, filter_=lambda node: searchterm.lower() == node.name.lower() )
            # filtredList = findall(partList, filter=lambda node: type in node.type )
            filtredList = []
            for parts in partList:
                if type in parts.type:
                    filtredList.append(parts)
            return filtredList
        else:
            partList = findall(self, filter_=lambda node: searchterm.lower() in node.name.lower() )
            filtredList = []
            for parts in partList:
                if type in parts.type:
                    filtredList.append(parts)
            return filtredList

    def findLeaves(self) -> "CreoNode":
        '''Searches part tree for all leaves (no children)'''
        leaves = []
        for CreoNode in self.descendants:  # walk down from the root
            # print(f'CreoNode.is_leaf {CreoNode.is_leaf} name {CreoNode.name} in {self.name}')
            if CreoNode.is_leaf:
                leaves.append(CreoNode)
        return leaves

    def findParts(self) -> "CreoNode":
        '''Searches part tree for all leaves (no children)'''
        parts = []
        for CreoNode in self.descendants:  # walk down from the root
            # print(f'CreoNode.is_leaf {CreoNode.is_leaf} name {CreoNode.name} in {self.name}')
            if CreoNode.is_leaf and CreoNode.type == "PRT":
                parts.append(CreoNode)
        return parts

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

    def fix_empty_asm(self) -> "CreoNode":
        allLeaves = self.findLeaves()
        for leaf in allLeaves:
            if leaf.type == "ASM" and leaf.depth == 1:
                logging.debug(f'Empty asm found: Name {leaf.name}.{leaf.type} #Children: {len(leaf.children)}. Empty={leaf.empty}')
                leaf.empty = True
                logging.debug(f'Empty asm found: Updated {leaf.name}.{leaf.type} to Empty={leaf.empty}')
    
    def find_childless_subAsm(self) -> "CreoNode":
        allLeaves = self.findLeaves()
        childlessSubAsm = []
        for leaf in allLeaves:
            if leaf.type == "ASM" and leaf.empty == False:
                logging.debug(f'Childless subasm {leaf.name}.{leaf.type}, # Children: {len(leaf.children)}, Empty={leaf.empty}')
                childlessSubAsm.append(leaf)
        return childlessSubAsm

    def isEmptySubAsm(self, asmName):
        emptyAsmNodes = self.findByName(type='ASM', searchterm=asmName, exact=True)

        for match in emptyAsmNodes:
            if match.is_leaf == True and match.empty == True:
                logging.debug(f'Empty SubAsm Found: {match.name} --- Leaf: {match.is_leaf == True} and Emtpy: {match.empty == True} = {match.is_leaf == True and match.empty == True}')
                return True
    
    def create_node_children(self, nodeContainer):
        '''Tagets a model node and searches nodeContainer for assemblies
        remaining BOM items, creates a copy of those assemblies
        and makes them children'''

        while True: # iterate across children until no more orphaned assemblies in BOM
            
            allChildlessSubAssemblies = self.find_childless_subAsm()
            logging.info(f'Number of childless sub: {len(self.find_childless_subAsm())}')

            childlessSubAssemblies = []

            for childlessSubAsm in allChildlessSubAssemblies:
                if nodeContainer.isEmptySubAsm(childlessSubAsm.name) != True:
                    childlessSubAssemblies.append(childlessSubAsm)
            logging.debug(f'# childlessSubAssemblies {len(childlessSubAssemblies)}')

            if len(childlessSubAssemblies) == 0: #####
                # break loop if no childless Subassemblies are found
                logging.info(f'Found no childless sub-assemblies...exiting: create_node_children()')
                break
            
            childlessSubAsmIter = 1
            for childlessSubAsm in childlessSubAssemblies:
                logging.info(f'Entering childlessSubAsmIter loop: Count {childlessSubAsmIter}')
                # Find all matches in name search of sub-assembly inported list and make list of matches of parents without children
                subAsmNodesMatches = nodeContainer.findByName(type='ASM', searchterm=childlessSubAsm.name, exact=True)
                
                bomMatches = []
                countMatch = 0
                # Log all matches from searching container for assembly name
                for match in subAsmNodesMatches:
                    countMatch += 1
                    logging.debug(f'SubAsm {childlessSubAsm.name}.{childlessSubAsm.type} Match# {countMatch}-> {match.name}.{match.type}, IsLeaf={match.is_leaf}, Empty={match.empty}')

                # Reduce matches to assemblies with children (ignores nodes that are at end of tree and marked as ASM with no children e.g. empty assemblies)
                countMatch = 0
                for match in subAsmNodesMatches:
                    countMatch += 1
                    if match.is_leaf == False and match.empty == False:
                        logging.info(f'{match.name}: {match.is_leaf == False} and {match.empty == False} = {match.is_leaf == False and match.empty == False}')
                        bomMatches.append(match)
                        
                    for match in bomMatches:
                        logging.debug(f'Found match without children {childlessSubAsm.name}.{childlessSubAsm.type}-> Match: {match.name}.{match.type}, IsLeaf={match.is_leaf}, Empty={match.empty}')

                if len(bomMatches) == 0:  # Check empty subassembly status if intentionally or missing tree items and exit
                    logging.info(f'len(bomMatches)==0 : {len(bomMatches) == 0}')
                    logging.info(f'No BOM matches Found {childlessSubAsm.name}. Empty={childlessSubAsm.empty}. #Children={len(childlessSubAsm.children)}')
                    
                    # Check if assembly is empty in node container

                    if nodeContainer.isEmptySubAsm(childlessSubAsm.name):
                        logging.info(f'Empty subasm {childlessSubAsm.name} ignored.')
                        break

                    else:
                        logging.critical('\n\nExiting: find_orphaned_subAsm()\n')
                        logging.critical(f'No children found for {childlessSubAsm.name}.{childlessSubAsm.type}. Empty={childlessSubAsm.empty}. #Children={len(childlessSubAsm.children)}')
                        logging.critical(f'{childlessSubAsm.getParentsPrintout()}')
                        exit()


                elif len(bomMatches) > 1:  # Check if we found multiple potential parents and exit if we did
                    logging.critical(f'len(bomMatches)>0 : {len(bomMatches) == 0}')
                    logging.critical(f'Found multiple sub-assemblies for {childlessSubAsm.name}')
                    for creoAsm in bomMatches:
                        logging.critical(f'{childlessSubAsm.name}.{childlessSubAsm.type} in {creoAsm.name}.{childlessSubAsm.type}')
                    exit()


                else: # for unique match, create a copy and assign to parent
                    logging.info(f'len(bomMatches)==1 : {not len(bomMatches) == 0}')
                    copySubAsm = bomMatches[0].__deepcopy__()
                    logging.info(f'Children found for {childlessSubAsm.name}.{childlessSubAsm.type}: Copying {copySubAsm.name}.{copySubAsm.type} #Chilren: {len(copySubAsm.children)}')
                    childlessSubAsm.children = copySubAsm.children
                    # print(childlessSubAsm.getParentsPrintout())
                    # subAsm.printTree()
                    # copySubAsm.printTree()
                
                childlessSubAsmIter += 1
                logging.info(f'Exiting childlessSubAsmIter loop')

