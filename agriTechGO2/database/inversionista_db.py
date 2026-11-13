from decimal import Decimal
from hashlib import sha256

from database.agricultor_db import abrir_bd, texto, numero


def iniciar_inversionista(usuario):
    usuario = texto(usuario, 100, obligatorio=True)
    identificador = sha256(usuario.casefold().encode("utf-8")).hexdigest()
    correo = f"demo-inv-{identificador}@example.invalid"

    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, correo, rol)
            VALUES (%s, %s, 'inversionista')
            ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)
            """,
            (usuario, correo),
        )

        cursor.execute(
            "SELECT id, activo FROM usuarios WHERE correo = %s",
            (correo,),
        )
        registro = cursor.fetchone()

        if not registro or not registro["activo"]:
            raise ValueError("El usuario de demostración está deshabilitado.")

        usuario_id = registro["id"]

        cursor.execute(
            """
            INSERT INTO perfiles (usuario_id)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE usuario_id = usuario_id
            """,
            (usuario_id,),
        )

        cursor.execute(
            """
            INSERT INTO wallets (usuario_id, saldo, es_simulada)
            VALUES (%s, 0, TRUE)
            ON DUPLICATE KEY UPDATE usuario_id = usuario_id
            """,
            (usuario_id,),
        )

    return usuario_id


def cargar_datos(usuario_id):
    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            SELECT u.nombre, p.descripcion, p.foto
            FROM usuarios u
            JOIN perfiles p ON p.usuario_id = u.id
            WHERE u.id = %s
            """,
            (usuario_id,),
        )
        perfil = cursor.fetchone()

        cursor.execute(
            "SELECT saldo FROM wallets WHERE usuario_id = %s",
            (usuario_id,),
        )
        wallet = cursor.fetchone()

        if perfil is None or wallet is None:
            raise ValueError("No se encontró el perfil o la wallet.")

        perfil["descripcion"] = perfil["descripcion"] or ""
        if perfil["foto"] is not None:
            perfil["foto"] = bytes(perfil["foto"])

        cursor.execute(
            """
            SELECT f.id, f.nombre, f.municipio, f.vereda,
                   u.nombre AS agricultor
            FROM fincas f
            JOIN usuarios u ON u.id = f.agricultor_id
            WHERE f.activa = TRUE AND u.activo = TRUE
            ORDER BY f.nombre
            """
        )
        fincas = cursor.fetchall()

        cursor.execute(
            """
            SELECT p.*,
                   COALESCE((
                       SELECT SUM(i.monto)
                       FROM inversiones i
                       WHERE i.proyecto_id = p.id
                         AND i.estado IN ('activa', 'finalizada')
                   ), 0) AS recaudado
            FROM proyectos p
            JOIN fincas f ON f.id = p.finca_id
            WHERE p.estado IN ('abierto', 'financiado', 'cerrado')
              AND p.es_simulado = TRUE
              AND f.activa = TRUE
            ORDER BY p.id
            """
        )
        proyectos = cursor.fetchall()

        cursor.execute(
            """
            SELECT finca_id FROM seguimientos
            WHERE inversionista_id = %s
            """,
            (usuario_id,),
        )
        siguiendo = {fila["finca_id"] for fila in cursor.fetchall()}

        cursor.execute(
            """
            SELECT i.id, f.nombre AS finca, p.titulo AS proyecto,
                   i.monto, i.rentabilidad_estimada, i.estado,
                   i.creado_en, i.es_simulada
            FROM inversiones i
            JOIN proyectos p ON p.id = i.proyecto_id
            JOIN fincas f ON f.id = p.finca_id
            WHERE i.inversionista_id = %s
            ORDER BY i.creado_en DESC, i.id DESC
            """,
            (usuario_id,),
        )
        inversiones = cursor.fetchall()

        cursor.execute(
            """
            SELECT creado_en, tipo, monto, detalle
            FROM movimientos_wallet
            WHERE usuario_id = %s
            ORDER BY creado_en DESC, id DESC
            """,
            (usuario_id,),
        )
        movimientos = cursor.fetchall()

    return {
        "perfil": perfil,
        "saldo": wallet["saldo"],
        "fincas": fincas,
        "proyectos": proyectos,
        "siguiendo": siguiendo,
        "inversiones": inversiones,
        "movimientos": movimientos,
    }


def guardar_perfil(usuario_id, nombre, descripcion):
    nombre = texto(nombre, 100, obligatorio=True)
    descripcion = texto(descripcion, 600)

    with abrir_bd() as (_, cursor):
        cursor.execute(
            "UPDATE usuarios SET nombre = %s WHERE id = %s",
            (nombre, usuario_id),
        )
        cursor.execute(
            """
            UPDATE perfiles
            SET descripcion = %s
            WHERE usuario_id = %s
            """,
            (descripcion, usuario_id),
        )


def guardar_foto(usuario_id, foto):
    if not foto or len(foto) > 2 * 1024 * 1024:
        raise ValueError("La foto debe pesar como máximo 2 MB.")

    with abrir_bd() as (_, cursor):
        cursor.execute(
            "UPDATE perfiles SET foto = %s WHERE usuario_id = %s",
            (foto, usuario_id),
        )


def cambiar_seguimiento(usuario_id, finca_id, seguir):
    with abrir_bd() as (_, cursor):
        if seguir:
            cursor.execute(
                "SELECT id FROM fincas WHERE id = %s AND activa = TRUE",
                (finca_id,),
            )
            if cursor.fetchone() is None:
                raise ValueError("La finca no está disponible.")

            cursor.execute(
                """
                INSERT INTO seguimientos (inversionista_id, finca_id)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE finca_id = finca_id
                """,
                (usuario_id, finca_id),
            )
        else:
            cursor.execute(
                """
                DELETE FROM seguimientos
                WHERE inversionista_id = %s AND finca_id = %s
                """,
                (usuario_id, finca_id),
            )


def mover_wallet(usuario_id, monto, tipo):
    monto = numero(monto, 2, "999999999999.99")

    if tipo not in ("recarga", "retiro"):
        raise ValueError("Tipo de movimiento no permitido.")

    with abrir_bd() as (_, cursor):
        cursor.execute("BEGIN PESSIMISTIC")

        cursor.execute(
            """
            SELECT saldo, es_simulada
            FROM wallets
            WHERE usuario_id = %s
            FOR UPDATE
            """,
            (usuario_id,),
        )
        wallet = cursor.fetchone()

        if not wallet or not wallet["es_simulada"]:
            raise ValueError("No se encontró una wallet de simulación.")

        movimiento = monto if tipo == "recarga" else -monto
        nuevo_saldo = wallet["saldo"] + movimiento

        if nuevo_saldo < 0:
            raise ValueError("Saldo insuficiente.")

        if nuevo_saldo > Decimal("999999999999.99"):
            raise ValueError("El saldo supera el máximo permitido.")

        cursor.execute(
            "UPDATE wallets SET saldo = %s WHERE usuario_id = %s",
            (nuevo_saldo, usuario_id),
        )
        cursor.execute(
            """
            INSERT INTO movimientos_wallet
                (usuario_id, tipo, monto, detalle)
            VALUES (%s, %s, %s, %s)
            """,
            (
                usuario_id,
                tipo,
                movimiento,
                "Recarga simulada" if tipo == "recarga" else "Retiro simulado",
            ),
        )


def invertir(usuario_id, proyecto_id, monto):
    monto = numero(monto, 2, "999999999999.99")

    with abrir_bd() as (_, cursor):
        cursor.execute("BEGIN PESSIMISTIC")

        # Bloquea el proyecto mientras se comprueba y registra el aporte.
        cursor.execute(
            "SELECT * FROM proyectos WHERE id = %s FOR UPDATE",
            (proyecto_id,),
        )
        proyecto = cursor.fetchone()

        if (
            not proyecto
            or proyecto["estado"] != "abierto"
            or not proyecto["es_simulado"]
        ):
            raise ValueError("El proyecto no está abierto para simulaciones.")

        cursor.execute(
            "SELECT activa FROM fincas WHERE id = %s FOR UPDATE",
            (proyecto["finca_id"],),
        )
        finca = cursor.fetchone()
        if not finca or not finca["activa"]:
            raise ValueError("La finca no está disponible.")

        cursor.execute(
            """
            SELECT monto FROM inversiones
            WHERE proyecto_id = %s
              AND estado IN ('activa', 'finalizada')
            FOR UPDATE
            """,
            (proyecto_id,),
        )
        recaudado = sum(
            (fila["monto"] for fila in cursor.fetchall()),
            Decimal("0"),
        )

        if monto > proyecto["meta"] - recaudado:
            raise ValueError(
                "El monto supera lo que falta para completar la meta. "
                "Actualiza la vista."
            )

        cursor.execute(
            """
            SELECT saldo, es_simulada FROM wallets
            WHERE usuario_id = %s
            FOR UPDATE
            """,
            (usuario_id,),
        )
        wallet = cursor.fetchone()

        if not wallet or not wallet["es_simulada"]:
            raise ValueError("No se encontró una wallet de simulación.")

        if monto > wallet["saldo"]:
            raise ValueError("Saldo insuficiente. Realiza una recarga simulada.")

        cursor.execute(
            """
            INSERT INTO inversiones (
                inversionista_id, proyecto_id, monto,
                rentabilidad_estimada, es_simulada
            )
            VALUES (%s, %s, %s, %s, TRUE)
            """,
            (
                usuario_id,
                proyecto_id,
                monto,
                proyecto["rentabilidad_estimada"],
            ),
        )
        inversion_id = cursor.lastrowid

        cursor.execute(
            "UPDATE wallets SET saldo = saldo - %s WHERE usuario_id = %s",
            (monto, usuario_id),
        )

        cursor.execute(
            """
            INSERT INTO movimientos_wallet (
                usuario_id, inversion_id, tipo, monto, detalle
            )
            VALUES (%s, %s, 'inversion', %s, %s)
            """,
            (
                usuario_id,
                inversion_id,
                -monto,
                f"Inversión simulada: {proyecto['titulo']}",
            ),
        )

        cursor.execute(
            """
            INSERT INTO seguimientos (inversionista_id, finca_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE finca_id = finca_id
            """,
            (usuario_id, proyecto["finca_id"]),
        )

        if recaudado + monto == proyecto["meta"]:
            cursor.execute(
                "UPDATE proyectos SET estado = 'financiado' WHERE id = %s",
                (proyecto_id,),
            )