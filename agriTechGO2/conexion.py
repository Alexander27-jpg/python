
import os
 
import mysql.connector
 
 
def _leer_credenciales():
    """Lee las credenciales de .streamlit/secrets.toml o de variables de entorno.
    Así la contraseña ya no queda escrita en el código ni en GitHub."""
    try:
        import streamlit as st
 
        cfg = st.secrets["tidb"]
        return {
            "host": cfg["host"],
            "port": int(cfg.get("port", 4000)),
            "user": cfg["user"],
            "password": cfg["password"],
            "database": cfg.get("database", "agritechgo"),
        }
    except Exception:
        pass
 
    # Alternativa: variables de entorno (por si corres crear_tablas.py suelto)
    try:
        return {
            "host": os.environ["gateway01.us-east-1.prod.aws.tidbcloud.com"],
            "port": int(os.environ.get("TIDB_PORT", 4000)),
            "user": os.environ["38EaRcZscBwS5ba.root"],
            "password": os.environ["qvVP8o2mkPeOro5H"],
            "database": os.environ.get("TIDB_DATABASE", "agritechgo"),
        }
    except KeyError as faltante:
        raise ConnectionError(
            f"Faltan las credenciales de TiDB (no existe {faltante}). "
            "Crea .streamlit/secrets.toml con la sección [tidb]."
        )
 
 
def obtener_conexion():
    """Devuelve una conexión a TiDB.
    Si falla, lanza ConnectionError con la causa REAL (antes devolvía None
    y el motivo solo salía en la terminal)."""
    credenciales = _leer_credenciales()
 
    try:
        conexion = mysql.connector.connect(
            **credenciales,
            ssl_disabled=False,
            ssl_verify_cert=True,
            connection_timeout=10,
        )
    except mysql.connector.Error as err:
        raise ConnectionError(f"TiDB rechazó la conexión: {err}") from err
 
    if not conexion.is_connected():
        raise ConnectionError("La conexión a TiDB se abrió pero no quedó activa.")
 
    return conexion