print("bienvenido a mmi codigo")
estudiantes = {
    1: "Ana",
    2: "Luis",
    3: "Carla",
    4: "Pedro",
    5: "Sofía"
}
asistencia = {
    "Lunes":     [1, 2, 3, 5],
    "Martes":    [1, 3, 4, 5],
    "Miércoles": [1, 2, 3],
    "Jueves":    [1, 2, 3, 4, 5],
    "Viernes":   [2, 3, 5]
}
for id_estudiante, nombre in estudiantes.items():
    dias_asistidos =0
    for dias, presentes in asistencia.items():
        if id_estudiante in presentes:
           dias_asistidos += 1
    promedio = (dias_asistidos / 5 ) *100
    if promedio <= 80 :
        print(f"Alerta {nombre} (ID: {id_estudiante}) tiene {promedio} de asistencia")