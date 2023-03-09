
class Format:
    def __init__(self, regex):
        self.regex = regex
        self.sims = {'(': 1, '|': 2, '.': 3, '*': 4, '+': 4, '?': 4}


    def prec(self, value):
        return 5 if value.isalnum() else self.sims[value]
    

    def positiveSus(self):
        string = self.regex
        stack = []
        while string.count('+') > 0:
            for i in range(len(string)):
                actual = string[i]
                if string[i] == '+':

                    if string[i-1].isalnum():
                        before = string[:i-1]
                        middle = string[i-1]
                        after = string[i+1:]
                        stack.append(middle)

                    elif string[i-1] == ')':
                        j = i-1
                        leftParen = string.count('(', 0, i)
                        countParen = 0
                        lastParenI = -20

                        while leftParen != countParen:
                            if string[j] == '(':
                                countParen += 1
                                lastParenI = j
                            if string[j] == '*':
                                break
                            j -= 1

                        if lastParenI != -20:
                            j = lastParenI-1

                        before = string[:j+1]
                        middle = string[j+1:i]
                        after = string[i+1:]
                        stack.append(middle)

                if  stack:
                    sus = stack.pop(0)
                    sus = sus*2
                    string = f'{before}({sus}*){after}'
        self.regex = string


    def zeroOrOneSus(self):
        string = self.regex
        stack = []
        while string.count('?') > 0:
            for i in range(len(string)):
                actual = string[i]
                if string[i] == '?':
                    if string[i-1].isalnum():
                        before = string[:i-1]
                        middle = string[i-1]
                        after = string[i+1:]
                        stack.append(middle)

                    elif string[i-1] == ')':
                        j = i-1
                        leftParen = string.count('(', 0, i)
                        countParen = 0

                        while leftParen != countParen:
                            if string[j] == '(':
                                countParen += 1
                            j -= 1

                        before = string[:j+1]
                        middle = string[j+1:i]
                        after = string[i+1:]
                        stack.append(middle)

                if  stack:
                    sus = stack.pop(0)
                    sus = f'({sus}|ε)'
                    string = f'{before}{sus}{after}'
        self.regex = string

    

    def concat(self):
        newRegex, ops = "", list(self.sims.keys())
        ops.remove('(')

        for i in range(len(self.regex)):
            # Caracter actual es val
            val = self.regex[i]
            if i+1 < len(self.regex):
                # Caracter siguiente es val_p1
                val_p1 = self.regex[i+1]
                newRegex += val

                # Validacion No. 1
                # Si el operador actual no es un parentesis que abre
                # y el siguiente no es un parentesis que cierra
                
                # Validacion No. 2
                # Si el carater actual no es un operador binario 
                # o no contiene al caracter de la izquierda

                # Validacion No. 3
                # Si los operadores no contienen al caracter de la derecha

                if val != '(' and val_p1 != ')' and val != '|' and val_p1 not in ops:
                    newRegex += '.'

        newRegex += self.regex[-1]
        return newRegex


    def infixPostfix(self):
        postfix, stack = '', []
        concatRegex = self.concat()

        for value in concatRegex:
            if value == '(':
                stack.append(value)

            elif value == ')':
                while stack[-1] != '(':
                    postfix += stack.pop()
                stack.pop()

            else:
                while stack and self.prec(value) <= self.prec(stack[-1]):
                    postfix += stack.pop()
                stack.append(value)

        while stack:
            postfix += stack.pop()
        return postfix



a = Format("(a|b)+(ab)+c?")
a.zeroOrOneSus()
a.positiveSus()
print(a.regex)
