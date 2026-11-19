import mysql.connector
import os

def obtener_conexion():
    try:
        # Asegúrate de colocar el archivo 'ca.pem' en la misma carpeta o ruta correcta
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ca_path = os.path.join(base_dir, "ca.pem")
        
        conexion = mysql.connector.connect(
            host="gateway01.us-east-1.prod.aws.tidbcloud.com",
            port=4000,
            user="38EaRcZscBwS5ba.root",
            password="AxJTDJtfhUwNPG70",
            database="agritechgo",
            ssl_disabled=False,
            ssl_ca=ca_path
        )
        if conexion.is_connected():
            return conexion
    except mysql.connector.Error as err:
        print(f"Error detallado de conexión: {err}")
        return None