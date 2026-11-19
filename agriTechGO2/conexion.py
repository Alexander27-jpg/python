import mysql.connector

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="gateway01.us-east-1.prod.aws.tidbcloud.com",
            port=4000,
            user="38EaRcZscBwS5ba.root",
            password="do7Qc4uEy06PcyVt",
            database="agritechgo",
            ssl_disabled=False,
            ssl_verify_cert=True
        )
        if conexion.is_connected():
            return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar con la base de datos: {err}")
        return None