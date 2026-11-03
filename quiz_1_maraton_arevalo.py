class maraton:
    def __init__(self):
        self.grupos =[]

    def registro(self):
        print("REGISTRO DE ESTUDIANTES")
        equipo = []

        for i in range(3):
            print(f" estudiante {i+1}:")
            nombre = input("Nombre: ")
            grado = int(input("Grado: "))
            colegio = input("Colegio: ")

            estudiantes = {
                "nombre": nombre,
                "Grado:": grado,
                "colegio": colegio
            }

            equipo.append(estudiantes)
        print("\n--- RESUMEN DEL EQUIPO ---")
        for estudiante in equipo:
            print(f"Nombre: {estudiante['nombre']} | Grado: {estudiante['Grado:']} | Colegio: {estudiante['colegio']}")
            
m = maraton()
m.registro()