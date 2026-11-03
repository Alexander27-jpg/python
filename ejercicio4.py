print("bienvenido a mi programa")
numero = int ( input("ingrese un numero: "))
suma = 0
pares = 0
impar = 0
for i in range(1, numero +1):
    print(i)
    suma += i

    if i % 2 == 0:
        pares += 1
    else:
        impar +=1
print("pares: " , pares)
print("impaeres: " , impar)
print("la suma total es: ", suma)
promedio = suma/numero
print("promedio: ",promedio)
    