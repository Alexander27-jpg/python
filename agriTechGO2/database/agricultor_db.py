from contextlib import contextmanager
from datetime import date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from uuid import uuid4

from conexion import obtener_conexion


@contextmanager
def abrir_bd():
    conexion = obtener_conexion()

    if conexion is None:
        raise ConnectionError("No se pudo conectar con TiDB.")

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("USE agritechgo")
        yield conexion, cursor
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            conexion.close()


def texto(valor, limite, obligatorio=False):
    resultado = str(valor or "").strip()

    if obligatorio and not resultado:
        raise ValueError("Completa los campos obligatorios.")

    if len(resultado) > limite:
        raise ValueError(f"Un campo supera el límite de {limite} caracteres.")

    return resultado


def numero(valor, decimales, maximo, permite_cero=False):
    try:
        resultado = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        raise ValueError("La cantidad o el precio no es válido.")

    if not resultado.is_finite():
        raise ValueError("La cantidad o el precio no es válido.")

    minimo_valido = resultado >= 0 if permite_cero else resultado > 0

    if not minimo_valido or resultado > Decimal(maximo):
        raise ValueError("La cantidad o el precio está fuera del rango permitido.")

    precision = Decimal("1").scaleb(-decimales)

    if resultado != resultado.quantize(precision):
        raise ValueError(f"Se permiten hasta {decimales} decimales.")

    return resultado


def obtener_productor_demo(usuario):
    """Identidad persistente exclusiva del acceso de demostración."""
    usuario = texto(usuario, 100, obligatorio=True)
    identificador = sha256(usuario.casefold().encode("utf-8")).hexdigest()
    correo_demo = f"demo-agri-{identificador}@example.invalid"

    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, correo, rol)
            VALUES (%s, %s, 'agricultor')
            ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)
            """,
            (usuario, correo_demo),
        )

        cursor.execute(
            "SELECT id, activo FROM usuarios WHERE correo = %s",
            (correo_demo,),
        )
        usuario_bd = cursor.fetchone()

        if not usuario_bd or not usuario_bd["activo"]:
            raise ValueError("El productor de demostración está deshabilitado.")

        return usuario_bd["id"]


def listar_cosechas(agricultor_id=None, solo_disponibles=False):
    sql = """
        SELECT c.*, f.nombre AS finca, f.agricultor_id,
               f.municipio, f.vereda
        FROM cosechas c
        JOIN fincas f ON f.id = c.finca_id
        WHERE 1 = 1
    """
    parametros = []

    if agricultor_id is not None:
        sql += " AND f.agricultor_id = %s"
        parametros.append(agricultor_id)

    if solo_disponibles:
        sql += " AND c.activa = TRUE AND c.cantidad > 0 AND f.activa = TRUE"

    sql += " ORDER BY c.creado_en DESC, c.id"

    with abrir_bd() as (_, cursor):
        cursor.execute(sql, tuple(parametros))
        registros = cursor.fetchall()

    for registro in registros:
        registro["activa"] = bool(registro["activa"])
        if registro["foto"] is not None:
            registro["foto"] = bytes(registro["foto"])

    return registros


def listar_fincas(agricultor_id):
    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            SELECT * FROM fincas
            WHERE agricultor_id = %s
            ORDER BY id
            """,
            (agricultor_id,),
        )
        return cursor.fetchall()


def leer_perfil(agricultor_id):
    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            SELECT u.nombre, p.telefono, p.municipio,
                   p.vereda, p.descripcion
            FROM usuarios u
            LEFT JOIN perfiles p ON p.usuario_id = u.id
            WHERE u.id = %s
            """,
            (agricultor_id,),
        )
        registro = cursor.fetchone()

        if registro is None:
            raise ValueError("No se encontró el productor.")

        cursor.execute(
            """
            SELECT nombre FROM fincas
            WHERE agricultor_id = %s
            ORDER BY id
            LIMIT 1
            """,
            (agricultor_id,),
        )
        finca = cursor.fetchone()

    perfil = {clave: valor or "" for clave, valor in registro.items()}
    perfil["finca_principal"] = finca["nombre"] if finca else ""
    return perfil


def guardar_perfil(agricultor_id, datos):
    nombre = texto(datos["nombre"], 100, True)
    telefono = texto(datos["telefono"], 25)
    municipio = texto(datos["municipio"], 80, True)
    vereda = texto(datos["vereda"], 100)
    descripcion = texto(datos["descripcion"], 600)
    finca = texto(datos["finca_principal"], 100, True)

    with abrir_bd() as (_, cursor):
        # Serializa los cambios del perfil de este productor.
        cursor.execute(
            "SELECT id FROM usuarios WHERE id = %s FOR UPDATE",
            (agricultor_id,),
        )
        if cursor.fetchone() is None:
            raise ValueError("No se encontró el productor.")

        cursor.execute(
            "UPDATE usuarios SET nombre = %s WHERE id = %s",
            (nombre, agricultor_id),
        )

        cursor.execute(
            """
            INSERT INTO perfiles
                (usuario_id, telefono, municipio, vereda, descripcion)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                telefono = %s, municipio = %s,
                vereda = %s, descripcion = %s
            """,
            (
                agricultor_id, telefono, municipio, vereda, descripcion,
                telefono, municipio, vereda, descripcion,
            ),
        )

        cursor.execute(
            """
            SELECT id FROM fincas
            WHERE agricultor_id = %s
            ORDER BY id LIMIT 1
            FOR UPDATE
            """,
            (agricultor_id,),
        )
        principal = cursor.fetchone()

        if principal:
            cursor.execute(
                """
                UPDATE fincas
                SET nombre = %s, municipio = %s, vereda = %s
                WHERE id = %s AND agricultor_id = %s
                """,
                (finca, municipio, vereda, principal["id"], agricultor_id),
            )
        else:
            cursor.execute(
                """
                INSERT INTO fincas
                    (agricultor_id, nombre, municipio, vereda)
                VALUES (%s, %s, %s, %s)
                """,
                (agricultor_id, finca, municipio, vereda),
            )


def registrar_cosecha(agricultor_id, datos):
    finca = texto(datos["finca"], 100, True)
    producto = texto(datos["producto"], 80, True)
    calidad = texto(datos["calidad"], 80, True)
    unidad = datos["unidad"]

    if unidad not in ("kg", "arroba", "unidad"):
        raise ValueError("Selecciona una unidad válida.")

    cantidad = numero(datos["cantidad"], 3, "999999999.999")
    precio = numero(datos["precio"], 2, "999999999999.99")

    if not isinstance(datos["fecha"], date):
        raise ValueError("Selecciona una fecha válida.")

    foto = datos.get("foto")
    if foto is not None and len(foto) > 2 * 1024 * 1024:
        raise ValueError("La fotografía debe pesar como máximo 2 MB.")

    cosecha_id = uuid4().hex

    with abrir_bd() as (_, cursor):
        # Reutiliza la finca si ese productor ya registró el mismo nombre.
        cursor.execute(
            """
            INSERT INTO fincas (agricultor_id, nombre)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)
            """,
            (agricultor_id, finca),
        )
        cursor.execute(
            """
            SELECT id, activa FROM fincas
            WHERE agricultor_id = %s AND nombre = %s
            FOR UPDATE
            """,
            (agricultor_id, finca),
        )
        finca_bd = cursor.fetchone()

        if not finca_bd["activa"]:
            raise ValueError("La finca está desactivada.")

        cursor.execute(
            """
            INSERT INTO cosechas (
                id, finca_id, producto, calidad, unidad,
                cantidad, precio, fecha, foto, activa
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            """,
            (
                cosecha_id, finca_bd["id"], producto, calidad,
                unidad, cantidad, precio, datos["fecha"], foto,
            ),
        )

    return cosecha_id


def actualizar_cosecha(
    agricultor_id, cosecha_id, cantidad, precio, activa
):
    cantidad = numero(cantidad, 3, "999999999.999", permite_cero=True)
    precio = numero(precio, 2, "999999999999.99")

    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            SELECT c.id
            FROM cosechas c
            JOIN fincas f ON f.id = c.finca_id
            WHERE c.id = %s AND f.agricultor_id = %s
            FOR UPDATE
            """,
            (cosecha_id, agricultor_id),
        )

        if cursor.fetchone() is None:
            raise ValueError("La cosecha no existe o pertenece a otro productor.")

        cursor.execute(
            """
            UPDATE cosechas
            SET cantidad = %s, precio = %s, activa = %s
            WHERE id = %s
            """,
            (cantidad, precio, bool(activa), cosecha_id),
        )

def publicar_proyecto(agricultor_id, finca_id, datos):
    titulo = texto(datos["titulo"], 150, obligatorio=True)
    descripcion = texto(datos["descripcion"], 2000, obligatorio=True)
    meta = numero(datos["meta"], 2, "999999999999.99")

    rentabilidad = numero(
        datos["rentabilidad_porcentaje"],
        2,
        "100",
        permite_cero=True,
    ) / Decimal("100")

    porcentaje_ventas = numero(
        datos["porcentaje_ventas"],
        2,
        "100",
        permite_cero=True,
    ) / Decimal("100")

    riesgo = datos["riesgo"]
    if riesgo not in ("Bajo", "Medio", "Alto"):
        raise ValueError("Selecciona un nivel de riesgo válido.")

    with abrir_bd() as (_, cursor):
        cursor.execute("BEGIN PESSIMISTIC")

        # Comprueba que la finca pertenezca a este productor.
        cursor.execute(
            """
            SELECT id
            FROM fincas
            WHERE id = %s
              AND agricultor_id = %s
              AND activa = TRUE
            FOR UPDATE
            """,
            (finca_id, agricultor_id),
        )

        if cursor.fetchone() is None:
            raise ValueError(
                "La finca no está activa o no pertenece a este productor."
            )

        # Evita repetir accidentalmente el mismo proyecto en la finca.
        cursor.execute(
            """
            SELECT id
            FROM proyectos
            WHERE finca_id = %s AND titulo = %s
            FOR UPDATE
            """,
            (finca_id, titulo),
        )
        if cursor.fetchall():
            raise ValueError(
                "Esta finca ya tiene un proyecto con ese título. "
                "Consulta los proyectos publicados."
            )

        cursor.execute(
            """
            INSERT INTO proyectos (
                finca_id,
                titulo,
                descripcion,
                meta,
                rentabilidad_estimada,
                riesgo,
                avance,
                porcentaje_ventas,
                estado,
                es_simulado
            )
            VALUES (%s, %s, %s, %s, %s, %s, 0, %s, 'abierto', TRUE)
            """,
            (
                finca_id,
                titulo,
                descripcion,
                meta,
                rentabilidad,
                riesgo,
                porcentaje_ventas,
            ),
        )
        proyecto_id = cursor.lastrowid

    return proyecto_id


def listar_proyectos_productor(agricultor_id):
    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            SELECT
                p.*,
                f.nombre AS finca,
                COALESCE((
                    SELECT SUM(i.monto)
                    FROM inversiones i
                    WHERE i.proyecto_id = p.id
                      AND i.estado IN ('activa', 'finalizada')
                ), 0) AS recaudado
            FROM proyectos p
            JOIN fincas f ON f.id = p.finca_id
            WHERE f.agricultor_id = %s
            ORDER BY p.creado_en DESC, p.id DESC
            """,
            (agricultor_id,),
        )
        return cursor.fetchall()

    
def listar_pedidos_agricultor(agricultor_id):
    """Consulta los pedidos recibidos por las cosechas del agricultor."""
    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            SELECT
                p.id,
                p.comprador_id,
                u.nombre AS comprador,
                p.cosecha_id,
                c.producto,
                c.finca_id,
                f.nombre AS finca,
                p.cantidad,
                p.unidad,
                p.precio_unitario,
                ROUND(p.cantidad * p.precio_unitario, 2) AS total,
                p.estado,
                p.creado_en
            FROM pedidos p
            JOIN usuarios u ON u.id = p.comprador_id
            JOIN cosechas c ON c.id = p.cosecha_id
            JOIN fincas f ON f.id = c.finca_id
            WHERE f.agricultor_id = %s
            ORDER BY
                CASE WHEN p.estado = 'pendiente' THEN 0 ELSE 1 END,
                p.creado_en DESC,
                p.id DESC
            """,
            (agricultor_id,),
        )
        return cursor.fetchall()


def aceptar_pedido(agricultor_id, pedido_id):
    """Acepta un pedido y descuenta el inventario en una transacción."""
    with abrir_bd() as (_, cursor):
        cursor.execute("BEGIN PESSIMISTIC")

        cursor.execute(
            """
            SELECT
                p.id,
                p.estado,
                p.cantidad AS cantidad_pedida,
                p.cosecha_id,
                c.cantidad AS cantidad_disponible,
                c.activa AS cosecha_activa,
                f.activa AS finca_activa,
                f.agricultor_id
            FROM pedidos p
            JOIN cosechas c ON c.id = p.cosecha_id
            JOIN fincas f ON f.id = c.finca_id
            WHERE p.id = %s
            FOR UPDATE
            """,
            (pedido_id,),
        )

        pedido = cursor.fetchone()

        if not pedido or pedido["agricultor_id"] != agricultor_id:
            raise ValueError(
                "El pedido no existe o no pertenece a tus cosechas."
            )

        if pedido["estado"] != "pendiente":
            raise ValueError(
                "Este pedido ya fue procesado anteriormente."
            )

        if not pedido["cosecha_activa"] or not pedido["finca_activa"]:
            raise ValueError(
                "La cosecha o la finca ya no están disponibles."
            )

        if pedido["cantidad_disponible"] < pedido["cantidad_pedida"]:
            raise ValueError(
                "No hay existencias suficientes para aceptar el pedido."
            )

        cursor.execute(
            """
            UPDATE cosechas
            SET cantidad = cantidad - %s
            WHERE id = %s AND cantidad >= %s
            """,
            (
                pedido["cantidad_pedida"],
                pedido["cosecha_id"],
                pedido["cantidad_pedida"],
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "No se pudo descontar el inventario. Actualiza los datos."
            )

        cursor.execute(
            """
            UPDATE pedidos
            SET estado = 'aceptado'
            WHERE id = %s AND estado = 'pendiente'
            """,
            (pedido_id,),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "El pedido cambió de estado. No se completó la operación."
            )


def rechazar_pedido(agricultor_id, pedido_id):
    """Rechaza un pedido pendiente sin descontar existencias."""
    with abrir_bd() as (_, cursor):
        cursor.execute("BEGIN PESSIMISTIC")

        cursor.execute(
            """
            SELECT p.id, p.estado, f.agricultor_id
            FROM pedidos p
            JOIN cosechas c ON c.id = p.cosecha_id
            JOIN fincas f ON f.id = c.finca_id
            WHERE p.id = %s
            FOR UPDATE
            """,
            (pedido_id,),
        )

        pedido = cursor.fetchone()

        if not pedido or pedido["agricultor_id"] != agricultor_id:
            raise ValueError(
                "El pedido no existe o no pertenece a tus cosechas."
            )

        if pedido["estado"] != "pendiente":
            raise ValueError(
                "Este pedido ya fue procesado anteriormente."
            )

        cursor.execute(
            """
            UPDATE pedidos
            SET estado = 'rechazado'
            WHERE id = %s AND estado = 'pendiente'
            """,
            (pedido_id,),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "No se pudo actualizar el estado del pedido."
            )

        
def listar_pagos_agricultor(agricultor_id):
    """Consulta los pagos recibidos por las cosechas del agricultor."""
    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            SELECT
                pa.id AS pago_id,
                pa.pedido_id,
                pa.monto,
                pa.estado,
                pa.referencia,
                pa.es_simulado,
                pa.creado_en,
                u.nombre AS comprador,
                c.producto,
                f.nombre AS finca,
                p.cantidad,
                p.unidad
            FROM pagos pa
            JOIN pedidos p ON p.id = pa.pedido_id
            JOIN usuarios u ON u.id = p.comprador_id
            JOIN cosechas c ON c.id = p.cosecha_id
            JOIN fincas f ON f.id = c.finca_id
            WHERE f.agricultor_id = %s
            ORDER BY pa.creado_en DESC, pa.id DESC
            """,
            (agricultor_id,),
        )
        return cursor.fetchall()

