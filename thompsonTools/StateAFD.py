
class StateAFD:

    def __init__(self, name, transitions, start=False, accepting=False):
        self.name = name
        self.transitions = transitions
        self.accepting = accepting
        self.start = start