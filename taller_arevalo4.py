print("bienvenido a mi codigo")
candidatos = ("andres", "felipe", "david")
votos = {"andres":0 , "felipe": 0, "david":0}
i = 0
while True:
    print(candidatos)
    presidente = input("por quien desea votar y si no quiere votar escribe FIN: ")
    if presidente == "andres":
        votos["andres"] +=1
    elif presidente == "felipe":
            votos["felipe"] +=1
    elif presidente == "david":
            votos["david"] +=1
    elif presidente == "FIN":
            break
    else: 
          print("ese no es un candidato")
ganador = max(votos, key=votos.get)
print(votos )
print("el ganador es: ",ganador)