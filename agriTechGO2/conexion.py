import mysql.connector

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="gateway01.us-east-1.prod.aws.tidbcloud.com",
            port=4000,
            user="38EaRcZscBwS5ba.root",
            password="AxJTDJtfhUwNPG70"
        )
        if conexion.is_connected():
            return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar con la base de datos: {err}")
        return None