
class Format:
    def __init__(self, regex):
        self.regex = regex
        self.sims = {'(': 1, '|': 2, '.': 3, '*': 4, '+': 4, '?': 4}


    def prec(self, value):
        return 5 if value.isalnum() else self.sims[value]
    
    def identitiesSus(self):
        string = self.regex
        stack = []
        while string.count('+') > 0:
            for i in range(len(string)):
                if string[i] == '+':
                    if string[i-1].isalnum():
                        before = string[:i-1]
                        middle = string[i-1]
                        stack.append(middle)
                        after = string[i+1:]
                    elif string[i-1] == ')':
                        j = i-1
                        # leftmost parenthesis
                        leftParen = string.count('(')
                        countParen = 0
 
                        while leftParen != countParen:
                            if string[j] == '(':
                                countParen += 1
                            j -= 1
                        # while string[j] != '(':
                        #     j -= 1
                        before = string[:j+1]
                        middle = string[j+1:i]
                        stack.append(middle)
                        after = string[i+1:]

                if  stack:
                    sus = stack.pop(0)
                    sus = sus*2
                    string = f'{before}({sus}*){after}'



        # for i in range(len(string)):
        #     if string[i] == '+':
        #         if string[i-1].isalnum():
                    
            #     elif string[i-1] == ')':
            #         j = i-1
            #         while string[j] != '(':
            #             j -= 1
            #         newString += f'({string[j:i]}*)'
            # else:
            #     newString += string[i]

        # for i in range(len(string)):
        #     if string[i] == '+' and string[i-1].isalnum():
        #         middle = string[i-1]*2
        #         before = string[:i-1]
        #         after = string[i+1:]
        #         string = f'{before}({middle}*){after}'


        #     elif string[i] == '+' and string[i-1] == ')':

        #         lParen = string.count('(')
        #         cParen = 0
        #         j = i-1
        #         while string[j] != '(' and lParen != cParen:
        #             if string[j] == '(':
        #                 cParen +=1
        #             j -= 1

        #         middle = string[j:i]*2
        #         before = string[:j]
        #         after = string[i+1:]
        #         string = f'{before}({middle}*){after}'

            # if string[i] == '?' and string[i-1].isalnum():
            #     middle = string[i-1]
            #     before = string[:i-1]
            #     after = string[i+1:]
            #     string = f'{before}({middle}|ε){after}'

            # elif string[i] == '?' and string[i-1] == ')':
            #     j = i-1
            #     while string[j] != '(':
            #         j -= 1

            #     middle = string[j:i]
            #     before = string[:j]
            #     after = string[i+1:]
            #     string = f'{before}({middle}|ε){after}'
            
        return string
        
    

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


a = Format("123x+++456")
print(a.identitiesSus())