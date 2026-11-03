print("bienvenido a mi codigo")
productos = {
    "electronica": ("Audífonos Bluetooth", 120000, True),
    "ropa": ("Camiseta", 45000, True),
    "hogar": ("Lámpara LED", 60000, False),
    "alimentos": ("Café Premium", 25000, False),
    "juguetes": ("Rompecabezas", 35000, True),
}
for nombre, precio, descuento in productos.values():
    if descuento == True:
        print(f"aplica descuento {nombre}")
        pagar = precio - (precio * 0.15) 
        print(f"valor a pagar {pagar}")
    elif descuento == False:
        print(f"no aplica descuento {nombre}")
        print(f"total a pagar {precio}")