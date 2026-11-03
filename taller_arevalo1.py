import itertools
print("bienvenido a mi codigo")
supermercado = {
        "manzana": [1200, 15],
        "leche": [3800, 10],
        "pan": [2000, 20],
        "arroz": [2500, 8]
    }
for i in itertools.count():
    print("_____________________________________")
    for producto, datos in supermercado.items():
        print(f"{producto.capitalize()}: precio = {datos[0]} cantidad = {datos[1]}")
    print("_____________________________________")
    producto = input("que producto desea llevar? ").lower()
    if producto in supermercado:
        cantidad = int(input("cuantos productos desea llevar? "))
        print("----COMPRA----")
        print("producto: ",producto.capitalize())
        print("precio: ", cantidad * supermercado[producto][0])
        print("SUPERMERCADO ACTUALIZADO")
        supermercado[producto][1]-= cantidad
        for producto, datos in supermercado.items():
            print(f"{producto.capitalize()}: precio =  {datos[0]} cantidad = {datos[1]} ")
        otra_compra = input("desea hacer otra compra: ").lower()
        if otra_compra == "no":
            break
    else: print("sea serio ese producto no esta")