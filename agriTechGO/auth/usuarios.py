import re

from mysql.connector import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from database import obtener_conexion


# Relaciona los nombres de las pantallas con los valores de MySQL.
ROLES = {
    "Agricultor / Caficultor": "agricultor",
    "Comprador Directo": "comprador",
    "Inversionista Agro": "inversionista",
    "Administradores (Equipo)": "administrador",
}

ETIQUETAS_ROL = {
    valor: etiqueta
    for etiqueta, valor in ROLES.items()
}

ROLES_REGISTRO = {
    "agricultor",
    "comprador",
    "inversionista",
}


def registrar_usuario(nombre, correo, password, etiqueta_rol):
    """Guarda la cuenta y su perfil en una misma transacción."""
    nombre = nombre.strip()
    correo = correo.strip().lower()
    rol = ROLES.get(etiqueta_rol.strip())

    if not nombre or len(nombre) > 100:
        raise ValueError("Escribe un nombre de entre 1 y 100 caracteres.")

    if (
        len(correo) > 150
        or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo)
    ):
        raise ValueError("Escribe un correo electrónico válido.")

    if not 12 <= len(password) <= 128:
        raise ValueError("La contraseña debe tener entre 12 y 128 caracteres.")

    if rol not in ROLES_REGISTRO:
        raise ValueError("Selecciona un perfil permitido para el registro.")

    password_hash = generate_password_hash(password, method="scrypt")
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO usuarios
                    (correo, password_hash, nombre, rol)
                VALUES (%s, %s, %s, %s)
                """,
                (correo, password_hash, nombre, rol),
            )

            usuario_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO perfiles (usuario_id) VALUES (%s)",
                (usuario_id,),
            )

            conexion.commit()
            return usuario_id

        finally:
            cursor.close()

    except IntegrityError as error:
        conexion.rollback()

        if error.errno == 1062:
            raise ValueError(
                "Ya existe una cuenta con ese correo."
            ) from error

        raise

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def autenticar_usuario(correo, password):
    """Devuelve los datos de una cuenta activa si la clave coincide."""
    correo = correo.strip().lower()

    if not correo or not password or len(password) > 128:
        return None

    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT id, correo, nombre, rol, password_hash, activo
                FROM usuarios
                WHERE correo = %s
                """,
                (correo,),
            )
            usuario = cursor.fetchone()

        finally:
            cursor.close()

    finally:
        conexion.close()

    if not usuario or not usuario["activo"]:
        return None

    try:
        clave_correcta = check_password_hash(
            usuario["password_hash"],
            password,
        )
    except (ValueError, TypeError):
        return None

    if not clave_correcta:
        return None

    # La contraseña protegida no pasa a la sesión de Streamlit.
    return {
        "id": usuario["id"],
        "correo": usuario["correo"],
        "nombre": usuario["nombre"],
        "rol": usuario["rol"],
    }