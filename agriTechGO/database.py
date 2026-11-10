import mysql.connector
import streamlit as st


def obtener_conexion():
    """Abre una conexión con la base de datos de agriTechGO."""
    configuracion = st.secrets["mysql"]

    return mysql.connector.connect(
        host=configuracion["host"],
        port=int(configuracion["port"]),
        user=configuracion["user"],
        password=configuracion["password"],
        database=configuracion["database"],
        charset="utf8mb4",
        connection_timeout=10,
        autocommit=False,
    )