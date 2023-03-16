
from Format import Format

class Node:
    def __init__(self, symbol, parent = None, left = None, right = None, no = None, anulable = False, firstpos = [], lastpos = []):
        self.symbol = symbol
        self.parent = parent
        self.left = left
        self.right = right
        self.no = no  
        self.anulable = anulable
        self.firstpos = firstpos
        self.lastpos = lastpos

class nextPos:
    def __init__(self, symbol, nextpos = []):
        self.symbol = symbol
        self.nextpos = nextpos        

class stateObj:
    def __init__(self, positions, transitions):
        self.positions = positions
        self.transitions = transitions


class AFD:
    def __init__(self, regex):
        self.regex = regex
        self.tree = None
        self.table = {}
        self.transitions = {}

    def augmentRegex(self):
        hashRegex = Format(self.regex + '#')
        hashRegex.idempotenciesApp()
        hashRegex.positiveId()
        hashRegex.zeroOrOneId()
        return hashRegex.concat()
    
    def syntaxTree(self):
        tree = []
        toDo = []
        enum = 1
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


    def firstPosMethod(self, tree):
        if tree:
            self.firstPosMethod(tree.left)
            self.firstPosMethod(tree.right)
            if tree.symbol.isalnum() and tree.no or tree.no == 0 or tree.symbol == '#':
                tree.firstpos = [tree.no]
            if tree.symbol == '|':
                tree.firstpos = tree.left.firstpos + tree.right.firstpos
            if tree.symbol == '.':
                if tree.left.anulable:
                    tree.firstpos = tree.left.firstpos + tree.right.firstpos
                else:
                    tree.firstpos = tree.left.firstpos
            if tree.symbol == '*':
                tree.firstpos = tree.left.firstpos
        return tree


    def lastPosMethod(self, tree):
        if tree:
            self.lastPosMethod(tree.left)
            self.lastPosMethod(tree.right)
            if tree.symbol.isalnum() and tree.no or tree.no == 0 or tree.symbol == '#':
                tree.lastpos = [tree.no]
            if tree.symbol == '|':
                tree.lastpos = tree.left.lastpos + tree.right.lastpos
            if tree.symbol == '.':
                if tree.right.anulable:
                    tree.lastpos = tree.left.lastpos + tree.right.lastpos
                else:
                    tree.lastpos = tree.right.lastpos
            if tree.symbol == '*':
                tree.lastpos = tree.left.lastpos
        return tree
    
    def genNextPosDict(self, tree):
        if tree:
            self.genNextPosDict(tree.left)
            self.genNextPosDict(tree.right)
            if tree.no or tree.no == 0:
                self.table[tree.no] = {tree.symbol: []}


    def genNextPos(self, tree):
        if tree:
            self.genNextPos(tree.left)
            self.genNextPos(tree.right)
            if tree.symbol == '.':
                for i in tree.left.lastpos:
                    for key in self.table[i]:
                        self.table[i][key] += tree.right.firstpos
            if tree.symbol == '*':
                for i in tree.lastpos:
                    for key in self.table[i]:
                        self.table[i][key] += tree.firstpos
        

    def tableToObj(self):
        for key in self.table:
            for key2 in self.table[key]:
                s = key2
                nP = self.table[key][key2]
                self.table[key] = nextPos(symbol=s, nextpos=nP)
        return self.table
        

    def symbolsDict(self):
        symbols = set()
        for i in range(len(self.table)):
            sym = self.table[i+1].symbol
            symbols.add(sym)
        symbols.remove('#')

        symbols = sorted(list(symbols))
        ts = {symbol: set() for symbol in symbols}
        # firstValue = self.table[1].nextpos
        return ts
    
    def genAFD(self, state=None):
        table = self.tableToObj()
        
        transitionTable = []
        states = []
        done = []
    
        if not state:
            firstValue = set(self.table[1].nextpos)
            symbols = self.symbolsDict()
            for num in firstValue:
                for key in symbols:
                    if table[num].symbol == key:
                        for el in table[num].nextpos:
                            symbols[key].add(el)
            stat = stateObj(firstValue, symbols)
            transitionTable.append(stat)
            for k, v in symbols.items():
                if v != firstValue and v:
                    states.append(v)

        while states:
            state = states.pop(0)
            symbols = self.symbolsDict()
            for num in state:
                for key in symbols:
                    if table[num].symbol == key:
                        for el in table[num].nextpos:
                            symbols[key].add(el)
            stat = stateObj(state, symbols)
            transitionTable.append(stat)
            done.append(state)
            for k, v in symbols.items():
                if v not in done and v:
                    states.append(v)
        return transitionTable


def printVisualTree(tree, level=0):
    if tree:
        printVisualTree(tree.right, level+1)
        if tree.no or tree.no == 0:
            print('  '*(level*3) + str(tree.symbol) + str(tree.no) + ' ' + str(tree.firstpos))
        else:
            print('  '*(level*3) + str(tree.symbol) + ' ' + str(tree.firstpos))
        printVisualTree(tree.left, level+1)


def printPostOrder(tree):
    if tree:
        printPostOrder(tree.left)
        printPostOrder(tree.right)
        print(tree.symbol)

            


afdd = AFD('(a|b)+abc?')
st = afdd.syntaxTree()
anulable = afdd.anulable(st[0])
fP = afdd.firstPosMethod(anulable)
lP = afdd.lastPosMethod(fP)

afdd.tree = fP
treeVar = afdd.tree
afdd.genNextPosDict(treeVar)
afdd.genNextPos(treeVar)
afdd.genAFD()
# afdd.tableToObj()
# afdd.transitionss()


# printVisualTree(fP)
