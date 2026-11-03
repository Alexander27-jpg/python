print("bienvendio al codigo")
empleados = [
    {"nombre": "Ana", "departamento": "Ventas", "salario": 2500000},
    {"nombre": "Luis", "departamento": "TI", "salario": 3200000},
    {"nombre": "Pedro", "departamento": "Ventas", "salario": 1800000},
    {"nombre": "Marta", "departamento": "TI", "salario": 4000000},
    {"nombre": "Sofia", "departamento": "RRHH", "salario": 2100000},
]
salarios = [emp["salario"] for emp in empleados]
promedio = sum(salarios) / len(salarios)
departamento = {}

for emp in empleados:
    if emp["salario"] > promedio:
        depto = emp["departamento"]
        if depto not in departamento:
            departamento[depto] = []
        departamento[depto].append(emp["nombre"])

print(f"Promedio general: {promedio}")
print(departamento)