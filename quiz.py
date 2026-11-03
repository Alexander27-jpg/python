#realiza un adgorimo en paython que permita clasificar una disquera, la cual tiene 5 artistas como 
#muchos años grabacion de albunes.
print("_______________________________________")
print("bienvenido a la disquera")
disquera = []
for i in range(5):
    artista = input(f"ingrese el artista {i+1} q desee registrar: ")
    cant_album = int( input("ingrese la cantidad de canciones del artista: "))
    genero = input("diguite el genero musical de su artista: ")
    año = int( input("diguite el año de salida del album: "))
    print("______________________________________________________________")

    archivo = {
        "artista:" :  artista,
        "cantidad de album: " : cant_album,
        "genero: " : genero,
        "año:" : año
    }
    disquera.append(archivo)

print("______________________________________________________________")
print("REGISTRO DE DATOS ")
for i in range(5):
    print (disquera[i])