import streamlit as st
import mysql.connector

from database import obtener_conexion


def verificar_base():
    """Consulta la base y sus tablas sin modificar datos."""
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT DATABASE()")
            base = cursor.fetchone()[0]

            cursor.execute("SHOW TABLES")
            tablas = [fila[0] for fila in cursor.fetchall()]

            return base, tablas
        finally:
            cursor.close()
    finally:
        conexion.close()


st.title("Prueba de conexión compartida")

if st.button("Probar database.py"):
    try:
        base, tablas = verificar_base()

    except mysql.connector.Error as error:
        st.error(f"Error de MySQL. Código: {error.errno}")

    except (FileNotFoundError, KeyError):
        st.error(
            "Revisa el archivo .streamlit/secrets.toml "
            "y su sección [mysql]."
        )

    else:
        st.success("¡La conexión desde database.py funciona!")
        st.write("Base de datos:", base)
        st.write("Tablas encontradas:", len(tablas))

        for tabla in tablas:
            st.write("•", tabla)