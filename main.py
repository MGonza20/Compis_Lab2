
from thompsonTools.Syntax import Syntax
from thompsonTools.AFN import AFN

class Compilador:
    def __init__(self):
        pass

    def menu(self):
        print("1. Visualizar AFD generado a partir del algoritmo de construccion de subconjuntos\n \
                  y su minimizacion\n")
        print("2. Visualizar AFD generado a partir del algoritmo de construccion directa y su minimizacion\n")
        print("2. Salir\n")
    
    def run(self):
        print("\n¡Bienvenid@ a la segunda aventura del dragon!\n")
        while True:
            self.menu()
            option = input("Opcion: ")
             
            if option == "1":
                string = input("Ingrese la expresion regular: ")
                syntax = Syntax(string)
                if string and syntax.checkParenthesis() \
                   and syntax.checkDot() \
                   and not syntax.checkMultU() \
                   and syntax.checkOperator() \
                   and syntax.checkOperatorValid() \
                   and syntax.checkLastNotU():
                    a = AFN(string)
                    a.graph_myt()
                else:
                    print("Expresion regular incorrecta\n")
            elif option == "2":
                print("¡Hasta luego!\n")
                break
            else:
                print("Opcion invalida, vuelva a ingresar nuevamente\n")

if __name__ == "__main__":
    c = Compilador()
    c.run()

