print("bienvendio a mi codigo")
oracion = input("Ingresa una oración: ").lower()

for s in ".,;:!?¿¡":
    oracion = oracion.replace(s, "")

palabras = oracion.split()
frecuencias = {}

for p in palabras:
    frecuencias[p] = frecuencias.get(p, 0) + 1

repetidas = [(p, v) for p, v in frecuencias.items() if v > 1]
print(repetidas)