#2. combinar dos diccionarios
#Escribe un programa que combine dos diccionarios. Si algun elemento está repetido, 
# el elemento del segundo diccionario debe sobrescribir del primero.

lista1 = {'a': 1, 'b': 2, 'c': 3}
lista2 = {'1': 20, 'd': 4}
resultado = {**lista1, **lista2}
print("Diccionario combinado:")
print(resultado)