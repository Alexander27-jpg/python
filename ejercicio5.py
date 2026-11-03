while True: 
    numero = int (input("digute el numero de tabla que desea generar: "))
    print("TABLA DEL ",numero)
    for i in range(11):
        print(numero, "x" , i, "=" , numero * i)
