# Define part classes
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
        if type(partName) != type('string'):
            return            
        partName = partName.lower()
        # partType = self.type
        partList = self.findByName(partName, type, exact=False)
        strNames = []
        for node in partList:
            strNames.append({'name':node.name, 'type':node.type, 'path': node.getParentsPrintout})
        return partList
    
    def findByName(self, type='', searchterm='', exact=False):
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
                logging.info(f'Empty asm found: Name {leaf.name}.{leaf.type} #Children: {len(leaf.children)}. Empty={leaf.empty}')
                leaf.empty = True
                logging.info(f'Empty asm found: Updated {leaf.name}.{leaf.type} to Empty={leaf.empty}')
    
    def find_orphaned_subAsm(self) -> "CreoNode":
        allLeaves = self.findLeaves()
        orphanedSubAsm = []
        for leaf in allLeaves:
            if leaf.type == "ASM" and leaf.empty != True:
                logging.debug(f'Orphaned subasm {leaf.name}.{leaf.type}, # Children: {len(leaf.children)}, Empty={leaf.empty}')
                orphanedSubAsm.append(leaf)
        return orphanedSubAsm

    # def find_missing_children(self) -> "CreoNode":
        missingChildren = []
        for CreoNode in self.descendants:  # walk down from the root
            if (CreoNode.type[0] == 'P'):  # Ignore parts
                continue
            if CreoNode.is_leaf:
                missingChildren.append(CreoNode)
        for child in missingChildren:
            logging.info(f'Missing child: {child.type} | {child.name}')
            print(f'{child.children}')
        return missingChildren

    # def fix_missing_children(self):
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

    def create_node_children(self, nodeContainer):
        '''Tagets a model node and searches nodeContainer for assemblies
        remaining BOM items, creates a copy of those assemblies
        and makes them children'''

        while True: # iterate across children until no more orphaned assemblies in BOM
            
            subAssemblies = self.find_orphaned_subAsm()
            logging.info(f'Length of ophaned sub: {len(self.find_orphaned_subAsm())}')

            if len(subAssemblies) == 0:
                # break 
                continue

            for subAsm in subAssemblies:
                subAsmNodesMatches = nodeContainer.findByName(type='ASM', searchterm=subAsm.name, exact=True)
                
            ##################### STILL DEBUGGING #######################

                bomMatches = []
                for match in subAsmNodesMatches:
                    if match.is_leaf != True and match.empty == False:
                        logging.info(f'Found match {subAsm.name}.{subAsm.type}-> {match.name}.{match.type}, IsLeaf={match.is_leaf}, Empty={match.empty}')
                        bomMatches.append(match)

                    for match in bomMatches:
                        logging.info(f'Found match {subAsm.name}.{subAsm.type}-> {match.name}.{match.type}, IsLeaf={match.is_leaf}, Empty={match.empty}')

                if len(bomMatches) == 0:  # Check empty subassembly status if intentionally or missing tree items and exit
                    logging.info(f'No BOM matches Found {subAsm.name}. Empty={subAsm.empty}. #Children={len(subAsm.children)}')

                    if subAsm.empty == False:
                        subAsm.printTree()
                        logging.critical('\n\nExiting: find_orphaned_subAsm()\n')
                        logging.critical(f'No children found for {subAsm.name}.{subAsm.type}. Empty={subAsm.empty}. #Children={len(subAsm.children)}')
                        logging.critical(f'{subAsm.getParentsPrintout()}')
                        exit()

                    else:
                        logging.info(f'Empty subasm {subAsm.name} ignored. Empty {subAsm.empty}')
                    continue
                    print('continue')


                elif len(bomMatches) > 1:  # Check if we found multiple potential parents and exit if we did
                    logging.critical(f'Found multiple sub-assemblies for {subAsm.name}')
                    for creoAsm in bomMatches:
                        logging.critical(f'{subAsm.name}.{subAsm.type} in {creoAsm.name}.{subAsm.type}')
                    exit()


                else: # for unique match, create a copy and assign to parent
                    copySubAsm = bomMatches[0].__deepcopy__()
                    subAsm.children = copySubAsm.children
                    logging.info(f'Children found for {subAsm.name}.{subAsm.type}: {copySubAsm.name}.{subAsm.type}')
                    # print(subAsm.getParentsPrintout())
                    subAsm.printTree()
                    # copySubAsm.printTree()
            # self.printTree()


