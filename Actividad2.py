#1. Hacer un programa que solicite por teclado dos número y muestre la suma, la resta,
#la multiplicación y la división de esos números
print("BIENVENIDO A MI PROGRAMA")
numero1 = int( input("numero 1:"))
numero2= int( input("numero 2:"))
suma = numero1 +numero2
print("_________________________SUMANDO_________________________")
print("total:",suma)
print("_________________________________________________________")

#2. Hacer un programa que solicite una edad y determine si es mayor de edad.
print("BIENVENIDO A MI PROGRAMA")
edad = int( input("ingrese su edad: "))
if edad >= 18:
    print("usted es mayor de edad")
else:
    print("usted es menor de edad")
print("_________________________________________________________")

#3. Hacer un programa que solicite una edad e imprima “Es mayor” si es mayor de
#edad, sino que imprima “Es menor”.
print("BIENVENIDO A MI PROGRAMA")
edad1 = int (input("ingrese una edad: "))
if edad1 >= 18:
    print("es mayor")
else: 
    print("es menor")
print("_________________________________________________________")

#4. Hacer un programa que solicite un color por teclado e imprima “Puede pasar “ si el
#color ingresado es verde, “Precaución “ si es amarillo, “No pasar “ si es rojo o “Color
#inválido” si es cualquier otro.
print("BIENVENIDO A MI PROGRAMA")
color = input(" ingrese un color: ")
if color == "verde": 
    print("puede pasar")
elif color == "amarillo": 
    print("precaución")
elif color == "rojo":
    print("no pasar")
else: 
    print("color desconocido")
print("_________________________________________________________")

#5. Hacer un programa que cuente desde el 1 al 100 y los imprima uno a uno
print("BIENVENIDO A MI PROGRAMA")
for i in range (1, 101):
    print(i)
print("_________________________________________________________")

#6. Hacer un programa que cuente del 1 al 100 inclusive e imprima sólo los números
#pares.
print("BIENVENIDO A MI PROGRAMA")
for i in range (1 , 101):
    if i % 2 == 0:
        print(i)
print("_________________________________________________________")

#7. Hacer un programa que cuente del 1 al 100 inclusive e imprima los números que son divisibles
#por 2 y por 5. 
print("BIENVENIDO A MI PROGRAMA")
for i in range (1, 101):
    if i % 2 == 0 and i % 5 == 0:
        print(i)
print("_________________________________________________________")

#8. Hacer un programa que imprima una tabla de mul>plicar del 2 al 9 . Cada uno debe mostrar sus
#valores mul>plicados del 1 al 9 inclusive
print("BIENVENIDO A MI PROGRAMA")
for i in range (2 , 10):
    print("TABLA DEL ",i)
    for j in range (1 , 10):
        print(i, "x" , j , " = ", i*j)
print("_________________________________________________________")
 