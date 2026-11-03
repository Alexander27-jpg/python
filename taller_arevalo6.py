print("bienvenido al codigo")
agenda = {
    "Ana": [{"telefono": "3001234567", "correo": "ana@mail.com"}],
    "Luis": [{"telefono": "3109876543", "correo": "luis@mail.com"}],
}
while True:
    print("__________________________")
    print("AGENDA DE CONTACTOS")
    print("1. Buscar contacto")
    print("2. Ver la agenda")
    print("3. Salir")
    print("__________________________")
    respuesta = int(input("elije una opcion: "))

    if respuesta == 3: 
        print("adios")
        break
    elif respuesta == 2:
        for nombre, datos in agenda.items():
              print(f"{nombre}: tel = {datos[0]["telefono"]} correo:{datos[0]["correo"]}")
    elif respuesta == 1:
         nombre = input("a quien desea buscar: ").capitalize()
         if nombre in agenda:
              print(f"tel: {agenda[nombre][0]["telefono"]}")
              print(f"correo: {agenda[nombre][0]["correo"]}")
         else: 
            print(f"'{nombre} no está en la agenda.")
            respuesta = input("¿Deseas agregarlo? : ").lower()
            if respuesta == "si":
                 telefono = input("Teléfono: ")
                 correo = input("Correo: ")
                 agenda[nombre] = [{"telefono": telefono, "correo": correo}]
                 print(f"'{nombre}' agregado a la agenda.")
