
class Node:
    def __init__(self, symbol, parent = None, enum = None, anulable = False, firstpos = None, lastpos = None):
        self.symbol = symbol
        self.parent = parent
        self.children = []
        self.enum = enum  
        self.anulable = anulable
        self.firstpos = firstpos
        self.lastpos = lastpos
        