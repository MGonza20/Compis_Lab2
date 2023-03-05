
# Description: Esta clase es usada para representar una transicion
# entre dos estados en un AFN.
class Bridge:
    def __init__(self, start, end, trs):
        self.start = start 
        self.end = end
        self.trs = trs
        