
from .Format import Format
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz/bin'    
from .StateAFD import StateAFD

import pydot
import networkx as nx
from graphviz import Digraph


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
        states = [self.tree.firstpos]
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
        
        # Changing the name of the states
        count = 0
        for state in newAFD:
            for st in newAFD:
                for key, transition in st.transitions.items():
                    if transition == set(state.name):
                        st.transitions[key] = chr(65+count)
            state.name = chr(65+count)
            count += 1

        return newAFD
    

    def minimizationAFD(self):
        # Creando copia del AFD
        afd = self.genAFD()

        # Unir estados de aceptacion y que no son de aceptacion
        accepting_states = set(state for state in afd if state.accepting)
        non_accepting_states = set(state for state in afd if not state.accepting)
        state_groups = [accepting_states, non_accepting_states]

        # Repetir hasta que no se puedan unir mas estados
        while True:
            new_state_groups = []
            for group in state_groups:
                # Por cada grupo de estados, agrupar por transiciones
                transition_groups = {}
                for state in group:
                    transition = tuple(sorted(state.transitions.values()))
                    if transition not in transition_groups:
                        transition_groups[transition] = set()
                    transition_groups[transition].add(state)

                # Por cada grupo de transiciones, unir estados
                for transition_group in transition_groups.values():
                    if len(transition_group) > 1:
                        new_state_groups.append(transition_group)
                    else:
                        new_state_groups.append({transition_group.pop()})

            # Si ya no se pueden unir mas estados, terminar
            if len(new_state_groups) == len(state_groups):
                break
            state_groups = new_state_groups

        # Crear nuevo AFD
        statesI = sum(len(group) for group in state_groups)
        reps = {}
        for group in state_groups:
            if len(group) > 1:
                same = []
                for element in group:
                    same.append(element)
                reps[chr(65+statesI)] = tuple(same)
                statesI += 1


        for replacement, same in reps.items():
            check = tuple([obj.name for obj in same])
            checkAccepting = tuple([obj.accepting for obj in same])
            checkStart = tuple([obj.start for obj in same])
            for key, state in afd.items():
                for k, v in state.transitions.items():
                    if v in check:
                        state.transitions[k] = replacement
                if  checkAccepting.count(True) > 0:
                    if state.name in check:
                        state.accepting = True
                if checkStart.count(True) > 0:
                    if state.name in check:
                        state.start = True
                if state.name in check:
                    state.name = replacement

        miniAFD = {}
        index = 0
        for state in afd:
            if state.name not in [obj.name for obj in miniAFD.values()]:
                miniAFD[index] = state
                index += 1

        return miniAFD



    def draw_afd(self, afd):

        G = nx.MultiGraph()
        for state in afd:
            if state.start:
                G.add_node(str(state.name), color='green', style='filled', shape='circle')
            if state.accepting:
                G.add_node(str(state.name), shape='doublecircle')
            for k, v in state.transitions.items():
                G.add_node(v)
                G.add_edge(str(state.name), str(v), label=k, dir='forward')
        
        dot = Digraph()
        for u, v, data in G.edges(data=True):
            dot.edge(u, v, label=data['label'], dir=data['dir'])
        for node in G.nodes:
            attrs = G.nodes[node]
            dot.node(node, **attrs)

        dot.attr(rankdir='LR')
        dot.render('directAFD/directAFD', format='png')


    def draw_mini_afd(self):
        afd = self.minimizationAFD()

        G = nx.MultiGraph()
        for state in afd.values():
            if state.start:
                G.add_node(state.name, color='green', style='filled', shape='circle')
            if state.accepting:
                G.add_node(state.name, shape='doublecircle')
            for k, v in state.transitions.items():
                if state.start:
                    G.add_node(state.name, color='green', style='filled', shape='circle')
                if state.accepting:
                    G.add_node(state.name, shape='doublecircle')
                else:
                    if v != 'estado muerto':
                        G.add_node(v)
                if v != 'estado muerto':
                    G.add_edge(state.name, v, label=k, dir='forward')
                   
        dot = Digraph()
        for u, v, data in G.edges(data=True):
            dot.edge(u, v, label=data['label'], dir=data['dir'])
        for node in G.nodes:
            attrs = G.nodes[node]
            dot.node(node, **attrs)

        dot.attr(rankdir='LR')
        dot.render('directAFD/miniDirectAFD', format='png')


    
    def simulateDirectAFD(self, string, afd):
        current_state = afd[0]
        for symbol in string:
            if symbol not in current_state.transitions:
                return False
            current_state = [afd[i] for i in range(len(afd)) if afd[i].name == current_state.transitions[symbol]]
            if not current_state:
                return False
            else:
                current_state = current_state[0]
        return current_state.accepting
    

    def simulateMiniAFD(self, string):
        afd = self.minimizationAFD()
        current_state = afd[0]
        for symbol in string:
            if symbol not in current_state.transitions:
                return False
            current_state = [state for key, state in afd.items() if state.name == current_state.transitions[symbol]]
            if not current_state:
                return False
            else:
                current_state = current_state[0]
        return current_state.accepting


    
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
        data = self.genAFD()
        self.draw_afd(data)

    
    def generateMiniAFD(self):
        st = self.syntaxTree()
        anulable = self.anulable(st[0])
        fP = self.firstPosMethod(anulable)
        lP = self.lastPosMethod(fP)
        self.tree = lP
        treeVar = self.tree
        self.genNextPosDict(treeVar)
        self.genNextPos(treeVar)
        self.tableToObj()
        self.draw_mini_afd()


    def simulateDirectAFD_General(self, miniString):
        st = self.syntaxTree()
        anulable = self.anulable(st[0])
        fP = self.firstPosMethod(anulable)
        lP = self.lastPosMethod(fP)
        self.tree = lP
        treeVar = self.tree
        self.genNextPosDict(treeVar)
        self.genNextPos(treeVar)
        self.tableToObj()
        data = self.genAFD()
        if self.simulateDirectAFD(miniString, data):
            print('Simulacion AFD Directo: Cadena aceptada')
        else:
            print('Simulacion AFD Directo: Cadena no aceptada')


    def simulateMiniAFD_General(self, miniString):
        st = self.syntaxTree()
        anulable = self.anulable(st[0])
        fP = self.firstPosMethod(anulable)
        lP = self.lastPosMethod(fP)
        self.tree = lP
        treeVar = self.tree
        self.genNextPosDict(treeVar)
        self.genNextPos(treeVar)
        self.tableToObj()
        data = self.genAFD()
        if self.simulateMiniAFD(miniString):
            print('Simulacion AFD Minimizado: Cadena aceptada')
        else:
            print('Simulacion AFD Minimizado: Cadena no aceptada')


        
        
    

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

            


afdd = AFD('(a*|b*)c')
var = 'ab'
# afdd.generateAFD()
afdd.simulateDirectAFD_General(var)
# afdd.generateMiniAFD()
afdd.simulateMiniAFD_General(var)

