print("bienvenido a mi codigo")
calificaciones = [("Ana", (85, 90, 78)), ("Luis", (60, 55,70))]
diccionario = {}
for nombre, nota in calificaciones:
    promedio = sum(nota) / len(nota)
    if promedio >= 70:
        estado = "aprobado"
    else: 
        estado = "reprobado"
    diccionario[nombre] = (promedio, estado)
print(diccionario)