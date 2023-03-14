
class Format:
    def __init__(self, regex):
        self.regex = regex
        self.sims = {'(': 1, '|': 2, '.': 3, '*': 4, '+': 4, '?': 4}


    def prec(self, value):
        return 5 if value.isalnum() else self.sims[value]


    def idempotenciesApp(self):
        regexStr = self.regex
        i = 0
        while i < len(regexStr)-1:
            if regexStr[i] == regexStr[i+1] and regexStr[i] in "+?":
                regexStr = regexStr[:i] + regexStr[i+1:]
            else:
                i += 1
        self.regex = regexStr


    def positiveId(self):
        expression = self.regex
        while '+' in expression:
            for i in range(len(expression)):

                if expression[i] == '+':
                    if expression[i-1] == ')':
                        j = i-2
                        continuee = True
                        closeParen = 1
                        while continuee:
                            if expression[j] == ')':
                                closeParen += 1
                            elif expression[j] == '(':
                                closeParen -= 1
                            j -= 1
                            if closeParen == 0:
                                continuee = False
                        expression = f'{expression[:j+1]}{expression[j+1:i]*2}*{expression[i+1:]}'

                    elif expression[i-1].isalnum():
                        before = expression[:i-1]
                        after = expression[i+1:]
                        middle = expression[i-1]*2
                        expression = f'{before}{middle}*{after}'    
            self.regex = expression

    
    def zeroOrOneId(self):
        expression = self.regex
        while '?' in expression:
            for i in range(len(expression)):

                if expression[i] == '?':
                    if expression[i-1] == ')':
                        j = i-2
                        continuee = True
                        closeParen = 1
                        while continuee:
                            if expression[j] == ')':
                                closeParen += 1
                            elif expression[j] == '(':
                                closeParen -= 1
                            j -= 1
                            if closeParen == 0:
                                continuee = False
                        expression = f'{expression[:j+1]}({expression[j+1:i]}|ε){expression[i+1:]}'

                    elif expression[i-1].isalnum():
                        before = expression[:i-1]
                        after = expression[i+1:]
                        middle = expression[i-1]
                        expression = f'{before}({middle}|ε){after}'    
            self.regex = expression


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



# a = Format("12c++(d|q)??e")
# a.zeroOrOneSus()
# a.positiveSus()
# print(a.regex)
# a.idempotenciesApp()
# a.zeroOrOneId()
# a.positiveId()
# print(a.infixPostfix())
# print(a.regex)
