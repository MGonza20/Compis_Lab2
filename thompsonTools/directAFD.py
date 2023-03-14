
from Format import Format

class Node:
    def __init__(self, symbol, parent = None, left = None, right = None, no = None): #, anulable = False, firstpos = None, lastpos = None):
        self.symbol = symbol
        self.parent = parent
        self.left = left
        self.right = right
        self.no = no  
        # self.anulable = anulable
        # self.firstpos = firstpos
        # self.lastpos = lastpos
        

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

        subexpr_stack = []  # stack to keep track of sub-expressions inside parentheses

        for i in range(len(regex)):
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
            if regex[i].isalnum():
                tree.append(Node(regex[i], no=enum))
                enum += 1
            elif regex[i] == '(':
                subexpr_stack.append(tree)  # push current subtree onto the stack
                tree = []  # start a new subtree for the sub-expression inside parentheses
            elif regex[i] == ')':
                # if regex[i+1] == '*':
                #     if len(tree) > 0:
                #         newSymK = Node(regex[i+1], left=tree[0])
                #         tree[0].parent = newSymK
                #         tree.append(newSymK)
                #         i += 1
                if len(subexpr_stack) > 0:
                    parent_tree = subexpr_stack.pop()  # pop the parent subtree from the stack
                    if len(tree) > 0:
                        
                        if regex[i+1] == '*':
                            parent_tree.append(Node(regex[i+1], left=tree[0]))
                            i += 1
                        else:
                            parent_tree.append(tree[0])  # add the current subtree as a child to the parent node
                    tree = parent_tree  # set the current subtree to the parent subtree
            elif regex[i] == '|' or regex[i] == '.':
                if len(tree) < 2:
                    toDo.append(regex[i])
        return tree

    

afdd = AFD('(a|b)+abc?')
aa = afdd.syntaxTree()
print(aa)
