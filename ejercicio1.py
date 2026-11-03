print("bienvenido a mi programa")
producto = input("ingrese el nombre del producto: ")
precio_unitario = float(input("ingrese el precio unitario: "))
cantidad = int(input("ingrese la cantidad: "))
subtotal = precio_unitario * cantidad
print("_______________________________________________________")
if subtotal > 100000:
    descuento = subtotal * 0.10
    print("descuento:", descuento)
    print("subtotal con descuento:", subtotal - descuento)
else:
    descuento = 0
    print("descuento:", descuento)
print("Producto:", producto)
print("Precio unitario:", precio_unitario)
print("Cantidad:", cantidad)
print("Subtotal:", subtotal)