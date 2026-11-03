# EJERCICIO 1: Dado un arreglo de temperaturas de una semana en Cúcuta,
# calcula la temperatura promedio, la máxima y el día (índice) en que ocurrió.
from array import array
temperaturas = [28.5, 30.2, 31.0, 29.8, 32.5, 33.1, 30.0]
promedio = sum(temperaturas)/len(temperaturas)
maxima = max(temperaturas)
indice = temperaturas.index(maxima)
print("Temperatura promedio:", promedio)
print("Temperatura maxima:", maxima)
print("Indice de Temperatura:", indice)