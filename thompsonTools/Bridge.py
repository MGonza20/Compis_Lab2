
# Description: Esta clase es usada para representar una transicion
# entre dos estados en un AFN.
class Bridge:
    def __init__(self, start, end, trs):
        self.start = start 
        self.end = end
        self.trs = trs
        self.syms = sorted(list({key2 for key1 in trs for key2 in trs[key1] if key2 != 'ε'}))
        