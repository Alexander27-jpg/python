print("bienvenido a mi programa")
calificaciones = []
for i in range(5):
    nota = float (input ("diguite 5 calificaciones: "))
    calificaciones.append(nota)
promedio = sum(calificaciones)/5
print("promedio: " ,promedio)

if promedio >= 3.0:
    print("aprobo")
else:
    print("reporbo")

if promedio >= 3.0 and promedio <= 3.5:
    print(" su promedio es basico ")
elif promedio > 3.5 and promedio < 4.5:
    print(" supromedio es bueno ")
elif promedio >= 4.5 and promedio <= 5.0:
    print("su promedio es excelente")
else: 
    print("ponga datos serios,")
print("calificaciones: ",calificaciones)
