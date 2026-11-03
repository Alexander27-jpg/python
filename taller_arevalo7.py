print("bienvenido al codigo")
estaciones = [
    (4.6, -74.1),    
    (40.7, -74.0),   
    (-33.9, 18.4),   
    (-15.8, -47.9),  
    (51.5, -0.1),    
]
hemisferios = {"Norte": [], "Sur": []}

for coordenada in estaciones:
    latitud = coordenada[0]

    if latitud >= 0:
        hemisferios["Norte"].append(coordenada)
    else:
        hemisferios["Sur"].append(coordenada)

print(hemisferios)