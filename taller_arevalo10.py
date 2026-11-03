print("bienvenido a mi codigo ")
diccionario = {
    "perro": "dog",
    "gato": "cat",
    "casa": "house"
}
while True:
    print("\n--- TRADUCTOR BÁSICO ---")
    print("1. Traducir una palabra")
    print("2. Agregar una nueva palabra")
    print("3. Ver palabras ordenadas alfabéticamente")
    print("4. Salir")
    
    opcion = input("Elige una opción (1-4): ")

    if opcion == "1":
        palabra = input("Ingresa la palabra a traducir: ").lower()
        if palabra in diccionario:
            print(f"Traducción: {palabra} -> {diccionario[palabra]}")
        else:
            print("La palabra no se encuentra en el diccionario.")

    elif opcion == "2":
        palabra_es = input("Palabra en español: ").lower()
        if palabra_es in diccionario:
            print("¡Atención! Esta palabra ya existe en el diccionario.")
        else:
            palabra_en = input("Traducción en inglés: ").lower()
            diccionario[palabra_es] = palabra_en
            print("Palabra agregada con éxito.")

    elif opcion == "3":
        palabras_ordenadas = sorted(list(diccionario.keys()))
        print("\nPalabras registradas alfabéticamente:")
        for palabra in palabras_ordenadas:
            print(f"- {palabra}: {diccionario[palabra]}")

    elif opcion == "4":
        print("Saliendo del traductor...")
        break
    else:
        print("Opción inválida, intenta de nuevo.")