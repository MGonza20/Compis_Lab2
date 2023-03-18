

from Bridge import Bridge
from Format import Format
from StateAFD import StateAFD
import pydot

import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz/bin'    

class AFN:
    def __init__(self, regex):
        self.regex = regex
        self.statesNo = 0
        self.afn = None
        self.afd = None

    def MYT(self):
        formatt = Format(self.regex)
        stringg = formatt.infixPostfix()
        stack = []

        for value in stringg:
            if value.isalnum(): 
                # Definiendo estados iniciales y finales
                start = self.statesNo
                end = self.statesNo + 1
                
                # Generando transicion
                transitions = {}
                # Formato: {estado inicial: {simbolo: [estado final]}}
                # Ejemplo: {0: {'a': [1]}}
                # Cuando se trata de un caracter solo hay un estado final e inicial
                transitions[start] = {value: [end]}
                
                # Se crea un objeto de tipo Bridge que es la transicion 
                # del caracter
                stack.append(Bridge(start, end, transitions))
                # Dado que se crearon dos estados se aumenta el contador en dos
                self.statesNo += 2

            elif value == '.':
                # # Obteniendo los dos ultimos elementos de la pila
                el2 = stack.pop()
                el1 = stack.pop()

                # Se realiza la union de los dos diccionarios para tomar 
                # en cuenta todas las transiciones
                el1.trs.update(el2.trs)

                # El objetivo de este ciclo es reemplazar el estado final
                # del primer elemento por el estado inicial del segundo
                for k, v in el1.trs.items():    
                    for el in v.values():
                        if el1.end in el:
                            dict1 = el1.trs[k]
                            key = list(dict1.keys())[0]
                            change = el1.trs[k][key].index(el1.end)
                            el1.trs[k][key][change] = el2.start
                            
                # Creando nuevo estado
                stack.append(Bridge(el1.start, el2.end, el1.trs))
                

            elif value == '|':
                # Obteniendo los dos ultimos elementos de la pila
                el2 = stack.pop()
                el1 = stack.pop()
                el1.trs.update(el2.trs)

                start = self.statesNo
                end = self.statesNo + 1
                
                # Caso: Union
                # Se crea un nuevo estado inicial con transicion epsilon a los dos estados iniciales
                # de los elementos del stack
                # y se crea una transicion epsilon de los estados finales de cada elemento del stack
                # hacia un nuevo estado final
                el1.trs.update({
                    start: {'ε': [el1.start, el2.start]},
                    el1.end: {'ε': [end]},
                    el2.end: {'ε': [end]}
                })

                # Creando nuevo estado
                stack.append(Bridge(start, end, el1.trs))
                self.statesNo += 2

            elif value == '*':
                # Obteniendo el ultimo elemento de la pila
                el1 = stack.pop()

                start = self.statesNo
                end = self.statesNo + 1
                self.statesNo += 2

                # Caso: Cerradura de Kleene
                # Se crea un nuevo estado inicial hacia el estado inicial del elemento del 
                # stack con transicion epsilon y tambien hacia un nuevo estado final

                # Se crea una transicion epsilon desde el estado final del elemento del stack
                # hacia su estado inicial y tambien hacia el nuevo estado final
                el1.trs.update({
                    start: {'ε': [el1.start, end]},
                    el1.end: {'ε': [el1.start, end]}
                })

                # Creando nuevo transicion
                stack.append(Bridge(start, end, el1.trs))

            elif value == '+':
                # Obteniendo el ultimo elemento de la pila
                el1 = stack.pop()
                start = self.statesNo
                end = self.statesNo + 1

                # Caso: Cerradura positiva
                # Se crea un nuevo estado inicial hacia el estado inicial del elemento del
                # stack con transicion epsilon, además sd genera una transicion epsilon desde
                # el estado final del elemento del stack hacia su estado inicial y hacia el
                # nuevo estado final 
                el1.trs.update({
                    start: {'ε': [el1.start]},
                    el1.end: {'ε': [el1.start, end]}
                })

                # Creando nuevo estado
                stack.append(Bridge(start, end, el1.trs))
                self.statesNo += 2
            
            elif value == '?':
                start = self.statesNo
                end = self.statesNo + 1
                self.statesNo += 2

                # Caso: ?
                # Dado que ? se refiere a que el caracter puede o no estar presente
                # o bien en otra representacion se refiere a: (caracter|ε)

                # Se genera una transicion epsilon desde un nuevo estado inicial 
                # hacia un nuevo estado final 
                transitions = {}
                transitions[start] = {'ε': [end]}
                
                el1 = stack.pop()
                el2 = Bridge(start, end, transitions)
                el1.trs.update(el2.trs)

                # Se realiza el mismo proceso que en el caso de la union
                start = self.statesNo
                end = self.statesNo + 1
                el1.trs.update({
                    start: {'ε': [el1.start, el2.start]},
                    el1.end: {'ε': [end]},
                    el2.end: {'ε': [end]}
                })

                # Creando nuevo estado
                stack.append(Bridge(start, end, el1.trs))
                self.statesNo += 2


        self.afn = stack.pop()
        return self.afn


    def graph_myt(self):
        myt = self.MYT()
        graph = pydot.Dot(graph_type='digraph', strict=True)
        graph.set_rankdir('LR')

        for k, v in myt.trs.items():
            for k2, v2 in v.items():
                for i in range(len(v2)):
                    if k == myt.start:
                        graph.add_node(pydot.Node(str(k), color='green', style='filled', shape='circle'))                                               
                    if v2[i] == myt.end:
                        graph.add_node(pydot.Node(str(v2[i]), shape='doublecircle'))
                    else:
                        graph.add_node(pydot.Node(str(v2[i])))
                    graph.add_edge(pydot.Edge(str(k), str(v2[i]), label=k2))
        graph.write_png('output1111.png', encoding='utf-8')


    def cerraduraKleene(self, state, checked=None):
        if not checked:
            checked = set()

        afn = self.afn
        transitions = afn.trs
        checked.add(state)

        for nextEp in transitions.get(state, {}).get('ε', []):
            if nextEp not in checked:
                checked.update(self.cerraduraKleene(nextEp, checked))
                
        return list(checked)
    

    def mover(self, state, symbol):
        afn = self.afn
        transitions = afn.trs
        return transitions.get(state, {}).get(symbol, [])
    
    def manyMove(self, states, symbol):
        move = [self.mover(state, symbol) for state in states]
        return list(set(sum(move, [])))
    
    def manyKleene(self, states):
        kleene = [self.cerraduraKleene(state) for state in states]
        return list(set(sum(kleene, [])))
        

    def toAFD(self):
        counter = 0
        afn = self.afn
        afd = {}
        start = afn.start
        symbols = afn.syms
        toDo = [self.cerraduraKleene(start)]
        checked = []

        while toDo:
            name = toDo.pop(0)
            if name not in checked:
                afdT = {symbol : self.manyKleene(self.manyMove(name, symbol)) for symbol in symbols}
                for state in afdT.values():
                        if len(state) > 0:
                            toDo.append(state)
                checked.append(name)
                afd[counter] = StateAFD(name, afdT, True) if counter == 0 else StateAFD(name, afdT)
                counter += 1

        for i in range(len(afd)):
            if afn.end in afd[i].name:
                afd[i].accepting = True
        self.afd = afd


    def createNewStates(self):
        sts = []
        afd = self.afd
        for i in range(len(afd)):
            if afd[i].name not in sts:
                sts.append(afd[i].name)
        letters = {}
        for i in range(len(sts)):
            letters[chr(65+i)] = sts[i]
        return letters
    

    def assignStates(self):
        afd = self.afd
        letters = self.createNewStates()
        for i in range(len(afd)):
            for k, v in letters.items():
                if afd[i].name == v:
                    afd[i].name = k
            for k, v in afd[i].transitions.items():
                for k2, v2 in letters.items():
                    if v == v2:
                        afd[i].transitions[k] = k2
                    elif not v:
                        afd[i].transitions[k] = 'estado muerto'
        return afd
    

    def minimizationAFD(self, afd):
        # Creando copia del AFD
        afd = self.assignStates().copy()

        # Unir estados de aceptacion y que no son de aceptacion
        accepting_states = set(state for key, state in afd.items() if state.accepting)
        non_accepting_states = set(state for key, state in afd.items() if not state.accepting)
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

        countStates = 0
        for i in range(len(state_groups)):
            countStates += len(state_groups[i])

        # Renombrando estados
        for group in state_groups:
            if len(group) > 1:
                name = chr(65+countStates)
                countStates += 1
                for st in group:
                    for key, value in afd.items():
                        if st.name in value.transitions.values():
                            for k, v in value.transitions.items():
                                if v == st.name:
                                    value.transitions[k] = name
                        if st.name == value.name:
                            value.name = name
        
        # Haciendo lista de repetidos
        repeated = []
        for i in range(len(state_groups)):
            if len(state_groups[i]) > 1:
                repeated.append(state_groups[i])
        
        unified = []
        for i in range(len(repeated)):
            countStart = 0
            countAccepting = 0
            startt = False
            acceptingg = False
            
            for j in range(len(repeated[i])):
                if list(repeated[i])[j].start:
                    countStart += 1
                if list(repeated[i])[j].accepting:
                    countAccepting += 1
            if countStart > 0:
                startt = True
            if countAccepting > 0:
                acceptingg = True
            unifiedState = StateAFD(list(repeated[i])[j].name, list(repeated[i])[j].transitions, startt, acceptingg)
            unified.append(unifiedState)
            
        
        # Eliminando estados repetidos
        for i in range(len(unified)):
            for key, value in afd.items():
                if unified[i].name == value.name:
                    afd[key] = unified[i]   

        miniAFD = {}
        for i in range(len(afd)):
            if afd[i] not in miniAFD.values():
                miniAFD[i] = afd[i]

        return miniAFD
    



    def draw_afd(self):
        afd = self.assignStates()

        graph = pydot.Dot(graph_type='digraph', strict=True)
        graph.set_rankdir('LR')

        for state in afd.values():
            for k, v in state.transitions.items():
                if state.start:
                    graph.add_node(pydot.Node(str(state.name), color='green', style='filled', shape='circle'))                                               
                if state.accepting:
                    graph.add_node(pydot.Node(str(state.name), shape='doublecircle'))
                else:
                    if v != 'estado muerto':
                        graph.add_node(pydot.Node(str(v)))
                if v != 'estado muerto':
                    graph.add_edge(pydot.Edge(str(state.name), str(v), label=k))
        graph.write_png('AfnToAfd.png', encoding='utf-8')

            


            
aff = AFN("(a|b)*abb")
aff.MYT()
# aff.graph_myt()
aff.toAFD()
newAFD = aff.minimizationAFD(aff.afd)
lett = 123

# aff.draw_afd()


        


