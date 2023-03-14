
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

        for i in range(len(regex)):
            if len(toDo) > 0:
                if toDo[-1] == '|':
                    if len(tree) > 1:
                        l = tree.pop(0)
                        r = tree.pop(0)
                        newSymU = Node(toDo.pop(), left = l, right = r) 
                        l.parent = newSymU
                        r.parent = newSymU
                        tree.append(newSymU)
                elif toDo[-1] == '.':
                    if len(tree) > 1:
                        l = tree.pop(0)
                        r = tree.pop(0)
                        newSymC = Node(toDo.pop(), left = l, right = r)
                        l.parent = newSymC
                        r.parent = newSymC
                        tree.append(newSymC)
            if regex[i].isalnum():
                tree.append(Node(regex[i], no = enum))
                enum += 1
            elif regex[i] == '|' or regex[i] == '.':
                if len(tree) < 2:
                    toDo.append(regex[i])
            if regex[i] == '*':
                children = tree.pop(0)
                newSym = Node(regex[i], left= children)
                children.parent = newSym
                tree.append(newSym) 
        return tree

    

afdd = AFD('(a|b)+abc?')
aa = afdd.syntaxTree()
print(aa)
