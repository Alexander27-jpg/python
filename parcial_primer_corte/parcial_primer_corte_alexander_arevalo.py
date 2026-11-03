print("bienvenido a mi codigo")
clientes = [{'id_cliente':100, 'edad': 28, 'productos':['P1', 'P2']},
                {'id_cliente':101, 'edad': 33, 'productos':['P3']},
                {'id_cliente':102, 'edad': 37, 'productos':['P1', 'P2', 'P5']},
                {'id_cliente':103, 'edad': 41, 'productos':['P3', 'P6']}
               ]
edad_cliente_dos = clientes[1]["edad"]
print(f"1. la edad del segundo cliente es: {edad_cliente_dos} años")

sumar= 0
print("2.")
for cliente in clientes:
    print(f"ID: {cliente["id_cliente"]}")
    sumar += cliente["edad"]
promedio = sumar / len(cliente)
print(f"3. promedio: {promedio}")

productos = []
for cliente in clientes:
    productos.extend(cliente["productos"])
print(f"4. lista de productos: {productos}")

productos_unicos = list(set(productos))
print(f"5. Productos únicos: {productos_unicos}")

for cliente in clientes:
    cliente['num_prod'] = len(cliente['productos'])
    cliente["activo"] = True

print("6. Estructura final con los campos añadidos:")
for cliente in clientes:
    print(cliente)