
from Format import Format

class Node:
    def __init__(self, symbol, parent = None, enum = None, anulable = False, firstpos = None, lastpos = None):
        self.symbol = symbol
        self.parent = parent
        self.children = []
        self.enum = enum  
        self.anulable = anulable
        self.firstpos = firstpos
        self.lastpos = lastpos
        

class AFD:
    def __init__(self, regex):
        self.regex = regex

    def augmentRegex(self):
        hashRegex = Format(self.regex + '#')
        hashRegex.idempotenciesApp()
        hashRegex.positiveId()
        hashRegex.zeroOrOneId()
        return hashRegex.concat()
    
    def syntaxTreeFromRegex(self):
        regex = self.augmentRegex()
        stack = []
        enum = 0
        for i in range(len(regex)):
            if regex[i].isalnum():
                node = Node(regex[i], enum = enum)
                stack.append(node)
                enum += 1
            elif regex[i] == '.':
                node = Node(regex[i])
                node.children.append(stack.pop())
                node.children.append(stack.pop())
                stack.append(node)
            elif regex[i] == '|':
                node = Node(regex[i])
                node.children.append(stack.pop())
                # node.children.append(stack.pop())
                stack.append(node)
            elif regex[i] == '*':
                node = Node(regex[i])
                node.children.append(stack.pop())
                stack.append(node)
            elif regex[i] == '#':
                node = Node(regex[i])
                node.children.append(stack.pop())
                stack.append(node)
        return stack.pop()
    

afdd = AFD('((12)|b)+abc?')
print(afdd.augmentRegex())

