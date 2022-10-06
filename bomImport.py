from lib.creoClass import CreoAsm
# from anytree import CreoAsm, RenderTree


if __name__ == '__main__':

    # Declare root
    root = CreoAsm(id='AsmRoot000')

    # Add parts
    subAsm010 = CreoAsm(id='SubAsm010', parent=root)
    subAsm020 = CreoAsm(id='subAsm020', parent=root)
    subAsm030 = CreoAsm(id='subAsm030', parent=root)
    part011 = CreoAsm(id='part011', parent=subAsm010)
    part012 = CreoAsm(id='part020', parent=subAsm010)
    part021 = CreoAsm(id='part021', parent=subAsm020)

    # Print Tree
    root.printTree()

    # print(RenderTree(root))