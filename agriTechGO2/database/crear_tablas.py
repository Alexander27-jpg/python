import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from conexion import obtener_conexion

def crear_tabla():
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            
            # 1. Creamos la base de datos si no existe
            cursor.execute("CREATE DATABASE IF NOT EXISTS agritechgo;")
            
            # 2. Seleccionamos la base de datos para trabajar dentro de ella
            cursor.execute("USE agritechgo;")
            
            # 3. Creamos la tabla de usuarios
            sql = """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                correo VARCHAR(100) UNIQUE NOT NULL,
                rol VARCHAR(50) NOT NULL
            );
            """
            cursor.execute(sql)
            print("¡Tabla 'usuarios' creada con éxito en la base de datos 'agritechgo'!")
            
        except Exception as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    crear_tabla()