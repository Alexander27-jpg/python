import os

import certifi
import mysql.connector


def _config():
    """Lee las credenciales de .streamlit/secrets.toml ([tidb]) o de variables de entorno."""
    try:
        import streamlit as st
        t = st.secrets["tidb"]
        return {
            "host": t["host"],
            "port": int(t.get("port", 4000)),
            "user": t["user"],
            "password": t["password"],
            "database": t["database"],
        }
    except Exception:
        return {
            "host": os.getenv("TIDB_HOST", "gateway01.us-east-1.prod.aws.tidbcloud.com"),
            "port": int(os.getenv("TIDB_PORT", "4000")),
            "user": os.getenv("TIDB_USER", ""),
            "password": os.getenv("TIDB_PASSWORD", ""),
            "database": os.getenv("TIDB_DATABASE", "agritechgo"),
        }


def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            **_config(),
            ssl_ca=certifi.where(),      # certificados raíz (TiDB Cloud usa Let's Encrypt / ISRG Root X1)
            ssl_verify_cert=True,
            connection_timeout=15,
        )
        if conexion.is_connected():
            return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar con la base de datos: {err}")
        return None


if __name__ == "__main__":
    # Prueba rápida:  python conexion.py
    c = obtener_conexion()
    print("✅ Conexión OK" if c else "❌ No conectó (revisa el mensaje de arriba)")
    if c:
        c.close()