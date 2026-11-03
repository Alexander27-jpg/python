while True: 
    class calculadora:
        def __init__(self):
                self.numeros = []

        
        def menu(self):
            print("bienvenido a la calculadora")
            print("===MENU===")
            print("1. sumar")
            print("2. restar")
            print("3. multiplicar")
            print("4. dividir")
            print("5. raiz")
            print("6. promedio")
            print("7. exponente")
            print("==========")

        def sumar(self, num1, num2):
            return num1 + num2

        def restar(self, num1, num2):
            return num1 - num2

        def multiplicar(self, num1, num2):
            return num1 * num2

        def dividir(self, num1, num2):
            return num1 / num2
    

        def raiz(self, numero1):
            return numero1 **0.5


        def promedio(self, lista):
            return sum(lista) / len(lista)

        def exponentes (self, num1, num2):
            return num1 ** num2 


    calculator = calculadora()
    calculator.menu()
    opcion = int(input("elija una opcion: "))

    if opcion == 1 or opcion == 2 or opcion == 3 or opcion == 4:

        num1 = float(input("ingrese el primer numero: "))
        num2 = float(input("ingrese el segundo numero: "))

        if opcion == 1:
            print(f"resultado: {calculator.sumar(num1,num2)}")

        elif opcion == 2:
            print(f" resultado: {calculator.restar(num1,num2)}")

        elif opcion == 3 :
            print(f"resultado: {calculator.multiplicar(num1,num2)}")

        elif opcion == 4:
            print(f"resultado: {calculator.dividir(num1,num2)}")

    if opcion == 5:
        numero1 = float(input("diguite el radicando de la raiz al cuadrada: "))
        print(f"resultado: {calculator.raiz(numero1)}")

    if opcion == 6: 
        numero2 = input(" ingrese los numero q quiere promeiar ejemplo ")
        lista = [float(n) for n in numero2.split()]
        print(f"resultado: {calculator.promedio(lista)}")

    if opcion == 7:
        base = float(input("diguite la base de la potencia: "))
        exponente = float(input("diguite el exponente de la potencia: "))
        print(f"resultado: {calculator.exponentes(base,exponente)}")

    pregunta = input("desea calcular otra cosa? (si, no): ").upper
    if pregunta == "NO":
        print("ADIOS")
        break
    else:
        print("ADIOS")
        break





    