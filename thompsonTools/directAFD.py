
from Format import Format
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz/bin'    
import pydot
from StateAFD import StateAFD

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

class npObj:
    def __init__(self, treeNo, symbol, nextpos = []):
        self.symbol = symbol
        self.nextpos = nextpos        
        self.treeNo = treeNo


class AFD:
    def __init__(self, regex):
        self.regex = regex
        self.tree = None
        self.table = {}
        self.tableSet = set()
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
                        if tree.right.firstpos not in self.table[i][key]:
                            self.table[i][key] += tree.right.firstpos
            if tree.symbol == '*':
                for i in tree.lastpos:
                    for key in self.table[i]:
                        if tree.firstpos not in self.table[i][key]:
                            self.table[i][key] += tree.firstpos
        

    def tableToObj(self):
        for key in self.table:
            for key2 in self.table[key]:
                s = key2
                nP = self.table[key][key2]
                self.tableSet.add(npObj(treeNo=key, symbol=s, nextpos=nP))
        return self.tableSet
        

    def genAFD(self):
        table = self.tableSet
        states = []
        toDo = [self.tree.firstpos]
        newAFD = []
        acceptState = None

        count = 0
        while toDo:
            toDoState = toDo.pop(0)
            symbols = {} 
            for elem in toDoState:
                for elem2 in table:
                    if elem == elem2.treeNo:
                        if elem2.symbol != '#':
                            if elem2.symbol not in symbols:
                                symbols[elem2.symbol] = set(elem2.nextpos)
                            else:
                                symbols[elem2.symbol].update(elem2.nextpos)
                            if list(symbols[elem2.symbol]) not in states:
                                states.append(list(symbols[elem2.symbol]))
                                toDo.append(list(symbols[elem2.symbol]))
                        else:
                            acceptState = elem2.treeNo
            newState = StateAFD(name=toDoState, transitions=symbols)
            if not count:
                newState.start = True
                count += 1
            newAFD.append(newState)

        for elem in newAFD:
            if acceptState in elem.name:
                elem.accepting = True
            
        return newAFD


    

    

    def drawAFD(self, table, initial, aceptting):
        graph = pydot.Dot(graph_type='digraph', strict=True)
        graph.set_rankdir('LR')
    
        for i in aceptting:
            graph.add_node(pydot.Node(i))
        graph.set_node_defaults(shape='circle')
        for k, v in table.items():
            for k2, v2 in v.transitions.items():
                if v.positions in aceptting:
                    graph.add_node(pydot.Node(str(v.positions), shape='doublecircle'))
                if v.positions == initial:
                    graph.add_node(pydot.Node(str(v.positions), color='green', style='filled', shape='circle'))
                else:
                    graph.add_node(pydot.Node(str(v.positions)))
                if v2 or v2 == 0:
                    graph.add_edge(pydot.Edge(v.positions, v2, label=k2))
        graph.write_png('afdDir.png')

    
    def generateAFD(self):
        st = self.syntaxTree()
        anulable = self.anulable(st[0])
        fP = self.firstPosMethod(anulable)
        lP = self.lastPosMethod(fP)
        self.tree = lP
        treeVar = self.tree
        self.genNextPosDict(treeVar)
        self.genNextPos(treeVar)
        self.tableToObj()
        symsssssssss = self.genAFD()
        table = self.genAFDTable([], self.tree.firstpos)
        # table, last = self.genAFD()
        # return self.createNewStates(table, last)
    

    def generatelP(self):
        st = self.syntaxTree()
        anulable = self.anulable(st[0])
        fP = self.firstPosMethod(anulable)
        lP = self.lastPosMethod(fP)
        return lP
    

    def defineInitialAndAceptting(self, table, initial, aceptting):
        for k, v in table.items():
            if v.positions == initial:
                v.initial = True
            if v.positions in aceptting:
                v.aceptting = True
        return table


    def minimizeAFD(self, table, groups=None):
        t = table
        if not groups:
            groups = [set(), set()]
            for k, v in t.items():
                if v.aceptting:
                    groups[0].add(v)
                else:
                    groups[1].add(v)
        return groups
        




def printVisualTree(tree, level=0):
    if tree:
        printVisualTree(tree.right, level+1)
        if tree.no or tree.no == 0:
            print('  '*(level*3) + str(tree.symbol) + str(tree.no) + ' ' + str(tree.lastpos))
        else:
            print('  '*(level*3) + str(tree.symbol) + ' ' + str(tree.lastpos))
        printVisualTree(tree.left, level+1)


def printPostOrder(tree):
    if tree:
        printPostOrder(tree.left)
        printPostOrder(tree.right)
        print(tree.symbol)

            


afdd = AFD('(a|b)+abc?')
data = afdd.generateAFD()
table = afdd.defineInitialAndAceptting(*data)
mini = afdd.minimizeAFD(table)
aa = 12
afdd.drawAFD(*data)