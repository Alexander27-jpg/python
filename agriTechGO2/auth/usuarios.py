import re
from contextlib import contextmanager

from werkzeug.security import generate_password_hash, check_password_hash

from conexion import obtener_conexion


ROLES_PUBLICOS = {
    "Agricultor / Caficultor": "agricultor",
    "Comprador Directo": "comprador",
    "Inversionista Agro": "inversionista",
}


@contextmanager
def abrir_bd():
    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No se pudo conectar con TiDB.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)
        yield conexion, cursor
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def registrar_usuario(correo, password):
    correo = correo.strip().lower()

    if len(correo) > 100 or not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", correo
    ):
        raise ValueError("Escribe un correo válido de máximo 100 caracteres.")

    if not 12 <= len(password) <= 128:
        raise ValueError("La contraseña debe tener entre 12 y 128 caracteres.")

    password_hash = generate_password_hash(password, method="scrypt")

    with abrir_bd() as (conexion, cursor):
        cursor.execute(
            """
            INSERT INTO usuarios (correo, password_hash, rol)
            VALUES (%s, %s, %s)
            """,
            (correo, password_hash, "pendiente"),
        )
        conexion.commit()


def autenticar_usuario(correo, password):
    correo = correo.strip().lower()

    if not correo or not password or len(password) > 128:
        return None

    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            SELECT id, nombre, correo, rol, activo, password_hash
            FROM usuarios
            WHERE correo = %s
            """,
            (correo,),
        )
        usuario = cursor.fetchone()

    if not usuario or not usuario["activo"]:
        return None

    password_hash = usuario.pop("password_hash", None)

    if not password_hash:
        return None

    try:
        coincide = check_password_hash(password_hash, password)
    except (ValueError, TypeError):
        return None

    return usuario if coincide else None


def consultar_usuario(usuario_id):
    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            SELECT id, nombre, correo, rol, activo
            FROM usuarios
            WHERE id = %s
            """,
            (usuario_id,),
        )
        return cursor.fetchone()


def asignar_rol_inicial(usuario_id, rol):
    if rol not in ROLES_PUBLICOS.values():
        raise ValueError("Ese perfil no está permitido.")

    with abrir_bd() as (conexion, cursor):
        cursor.execute(
            """
            UPDATE usuarios
            SET rol = %s
            WHERE id = %s
              AND rol = 'pendiente'
              AND activo = TRUE
            """,
            (rol, usuario_id),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "No se pudo asignar el perfil. Cierra sesión y vuelve a entrar."
            )

        conexion.commit()