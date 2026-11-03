class clases: 

    def evaluar(self, nota):
        if nota >= 3.0:
            return "gano la materia"
        elif nota < 3.0:
            return "pierde la materia"

    def menu(self):
        print("===MENU===")
        print("MATERIAS")
        print("1. Matematicas")
        print("2. Sociales")
        print("3. Eespañol")
        print("4. Quimica")
        print("5. Fisica")
        print("==========")
        
while True: 
    print("bienvenido al portal de calificaciones")
    inicio = clases()
    inicio.menu()

    opcion = int(input("elija la mateteria q desee revisar: "))

    calificacion = float(input("cual fue su nota promedio: "))

    if opcion == 1 or opcion == 2 or opcion == 3 or opcion == 4 or opcion == 5: 
        print(f"Resultado: {inicio.evaluar(calificacion)}")
        if calificacion < 3.0: 
            habilitar = input("Desea habilitar la materia: ").upper()
            if habilitar == "SI":
                calificacion_nueva = float(input("cual es su nuevo promedio: "))
                print(f"Resultado: {inicio.evaluar(calificacion_nueva)}")
            else:
                print("perdio la materia") 

        respuesta = input("desea mirar otra materia?: ").upper()
        if respuesta == "NO":
            break
