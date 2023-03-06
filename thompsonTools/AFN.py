

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
        graph.write_png('output.png', encoding='utf-8')


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
        return sum(move, [])
    
    def manyKleene(self, states):
        kleene = [self.cerraduraKleene(state) for state in states]
        return sum(kleene, [])
        

    def toAFD(self, counter=0):

        afn = self.afn
        start = afn.start
        symbols = afn.syms

        afd = {}

        if not afd:
            name = self.cerraduraKleene(start)
            afdT = {symbol : [] for symbol in symbols}
            for symbol in symbols:
                afdT[symbol] = self.manyKleene(self.manyMove(name, symbol))
            stateAFD = StateAFD(name, afdT)
            afd[counter] = (stateAFD)

        return afd



            


                



    
    
# aff = AFN("a?(b?)?a*")
# aff.MYT()
# print(aff.cerraduraKleene(4))

# aff = AFN("ab*ab*")
# aff.MYT()
# print(aff.cerraduraKleene(0))

aff = AFN("(a|b)*aab")
aff.MYT()
print(aff.toAFD())


        


