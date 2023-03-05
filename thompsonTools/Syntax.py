

class Syntax:
    def __init__(self, string): 
        self.string = string
        self.sims = {'(': 1, '|': 2, '.': 3, '*': 4, '+': 4, '?': 4}
        

    def checkParenthesis(self):
        stack = []
        for i in range(len(self.string)):
            if self.string[i] == '(': 
                stack.append(self.string[i])
            elif self.string[i] == ')':
                if not stack:
                    return False
                stack.pop()
        return not stack


    def checkOperator(self):
        for i in range(len(self.string)):
            if self.string[i] in self.sims.keys():
                if self.string[i] != '(':
                    if i == 0:
                        return False
        return True


    def checkOperatorValid(self):
        for i in range(len(self.string)):
            if not self.string[i].isalnum() and self.string[i] not in self.sims.keys() and self.string[i] != ')':
                return False
        return True
    
    
    def checkDot(self):
        for i in range(len(self.string)):
            if(self.string[i] == '.'):
                return False
        return True
    

    def checkMultU(self):
        count = 0
        for c in self.string:
            if c == '|':
                count += 1
                if count >= 2:
                    return True
            else:
                count = 0

    def checkLastNotU(self):
        if self.string[-1] == '|':
            return False
        return True
    