
from Format import Format

class Node:
    def __init__(self, symbol, parent = None, left = None, right = None, no = None, anulable = False, firstpos = [], lastpos = None):
        self.symbol = symbol
        self.parent = parent
        self.left = left
        self.right = right
        self.no = no  
        self.anulable = anulable
        self.firstpos = firstpos
        self.lastpos = lastpos
        

class AFD:
    def __init__(self, regex):
        self.regex = regex

    def augmentRegex(self):
        hashRegex = Format(self.regex + '#')
        hashRegex.idempotenciesApp()
        hashRegex.positiveId()
        hashRegex.zeroOrOneId()
        return hashRegex.concat()
    
    def syntaxTree(self):
        tree = []
        toDo = []
        enum = 0
        regex = self.augmentRegex()
        subexpr_stack = [] 

        for i in range(len(regex)):
            rrrr = regex[i]
            if len(toDo) > 0:
                if toDo[-1] == '|':
                    if len(tree) > 1:
                        l = tree.pop(0)
                        r = tree.pop(0)
                        newSymU = Node(toDo.pop(), left=l, right=r)
                        l.parent = newSymU
                        r.parent = newSymU
                        tree.append(newSymU)
                elif toDo[-1] == '.':
                    if len(tree) > 1:
                        l = tree.pop(0)
                        r = tree.pop(0)
                        newSymC = Node(toDo.pop(), left=l, right=r)
                        l.parent = newSymC
                        r.parent = newSymC
                        tree.append(newSymC)
            if regex[i].isalnum() or regex[i] == '#':
                if i+1 < len(regex) and regex[i+1] == '*':
                    if regex[i] != 'ε':
                        alnumNode = Node(regex[i], no=enum)
                        kleeneNode = Node(regex[i+1], left=alnumNode)
                        alnumNode.parent = kleeneNode
                        tree.append(kleeneNode)
                        enum += 1
                    else:
                        alnumNode = Node(regex[i])
                        kleeneNode = Node(regex[i+1], left=alnumNode)
                        alnumNode.parent = kleeneNode
                        tree.append(kleeneNode)
                else:
                    if regex[i] != 'ε':
                        alnumNode = Node(regex[i], no=enum)
                        tree.append(alnumNode)
                        enum += 1
                    else:
                        alnumNode = Node(regex[i])
                        tree.append(alnumNode)
            elif regex[i] == '(':
                subexpr_stack.append(tree)  
                tree = []  
            elif regex[i] == ')':
                if len(subexpr_stack) > 0:
                    parent_tree = subexpr_stack.pop()  
                    if len(tree) > 0:
                        if regex[i+1] == '*':
                            parent_tree.append(Node(regex[i+1], left=tree[0]))
                            i += 1
                        else:
                            parent_tree.append(tree[0])  
                    tree = parent_tree  
            elif regex[i] == '|' or regex[i] == '.':
                if len(tree) < 2:
                    toDo.append(regex[i])
        while toDo and tree:
            if toDo[-1] == '|':
                if len(tree) > 1:
                    l = tree.pop(0)
                    r = tree.pop(0)
                    newSymU = Node(toDo.pop(), left=l, right=r)
                    l.parent = newSymU
                    r.parent = newSymU
                    tree.append(newSymU)
            elif toDo[-1] == '.':
                if len(tree) > 1:
                    l = tree.pop(0)
                    r = tree.pop(0)
                    newSymC = Node(toDo.pop(), left=l, right=r)
                    l.parent = newSymC
                    r.parent = newSymC
                    tree.append(newSymC)
        return tree
    

    def anulable(self, tree):
        if tree:
            self.anulable(tree.left)
            self.anulable(tree.right)
            if tree.symbol == 'ε':
                tree.anulable = True
            elif tree.symbol.isalnum():
                tree.anulable = False
            elif tree.symbol == '|':
                    tree.anulable = tree.left.anulable or tree.right.anulable
            elif tree.symbol == '.':
                    tree.anulable = tree.left.anulable and tree.right.anulable
            elif tree.symbol == '*':
                tree.anulable = True
        return tree


    def firstpos(self, tree):
        if tree:
            self.firstpos(tree.left)
            self.firstpos(tree.right)
            if tree.symbol.isalnum():
                tree.firstpos.append(tree.no)
            elif tree.symbol == '|':
                tree.firstpos = tree.left.firstpos + tree.right.firstpos
            elif tree.symbol == '.':
                if tree.left.anulable:
                    tree.firstpos = tree.left.firstpos + tree.right.firstpos
                else:
                    tree.firstpos = tree.left.firstpos
            elif tree.symbol == '*':
                tree.firstpos = tree.left.firstpos 
        return tree                            


def printVisualTree(tree, level=0):
    if tree:
        printVisualTree(tree.right, level+1)
        if tree.no or tree.no == 0:
            print('  '*(level*3) + str(tree.symbol) + str(tree.no) + ' ' + str(tree.firstpos))
        else:
            print('  '*(level*3) + str(tree.symbol) +  ' ' + str(tree.firstpos))
        printVisualTree(tree.left, level+1)


def printPostOrder(tree):
    if tree:
        printPostOrder(tree.left)
        printPostOrder(tree.right)
        print(tree.symbol)

def printFirstPos(tree):
    if tree:
        printFirstPos(tree.left)
        printFirstPos(tree.right)
        if tree.symbol.isalnum() and tree.no or tree.no == 0 or tree.symbol == '#':
            # print(tree.symbol, [tree.no])
            tree.firstpos = [tree.no]
        if tree.symbol == '|':
            # print(tree.symbol, tree.left.firstpos + tree.right.firstpos)
            tree.firstpos = tree.left.firstpos + tree.right.firstpos
        if tree.symbol == '.':
            if tree.left.anulable:
                # print(tree.symbol, tree.left.firstpos + tree.right.firstpos)
                tree.firstpos = tree.left.firstpos + tree.right.firstpos
            else:
                # print(tree.symbol, tree.left.firstpos)
                tree.firstpos = tree.left.firstpos
        if tree.symbol == '*':
            # print(tree.symbol, tree.left.firstpos)
            tree.firstpos = tree.left.firstpos
    return tree

            


afdd = AFD('(a|b)+abc?')
st = afdd.syntaxTree()
anulable = afdd.anulable(st[0])
fP = printFirstPos(anulable)
# afdd.firstpos(aa[0])
# print('PostOrder')
printVisualTree(fP)
