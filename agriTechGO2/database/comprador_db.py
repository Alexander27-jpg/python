from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from database.reparto_db import repartir_pago
from database.agricultor_db import abrir_bd, texto, numero
from uuid import uuid4


def iniciar_comprador(usuario):
    """Recupera la identidad del comprador para el login de demostración."""
    usuario = texto(usuario, 100, obligatorio=True)
    identificador = sha256(usuario.casefold().encode("utf-8")).hexdigest()
    correo = f"demo-comp-{identificador}@example.invalid"

    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, correo, rol)
            VALUES (%s, %s, 'comprador')
            ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)
            """,
            (usuario, correo),
        )

        cursor.execute(
            "SELECT id, activo FROM usuarios WHERE correo = %s",
            (correo,),
        )
        comprador = cursor.fetchone()

        if not comprador or not comprador["activo"]:
            raise ValueError("El comprador está deshabilitado.")

        return comprador["id"]


def crear_pedido(
    comprador_id,
    cosecha_id,
    cantidad,
    precio_mostrado,
    unidad_mostrada,
):
    """Guarda una solicitud pendiente sin descontar inventario."""
    cantidad = numero(cantidad, 3, "999999999.999")
    precio_mostrado = numero(
        precio_mostrado, 2, "999999999999.99"
    )

    with abrir_bd() as (_, cursor):
        cursor.execute("BEGIN PESSIMISTIC")

        cursor.execute(
            """
            SELECT id FROM usuarios
            WHERE id = %s AND activo = TRUE AND rol = 'comprador'
            FOR UPDATE
            """,
            (comprador_id,),
        )
        if cursor.fetchone() is None:
            raise ValueError("El comprador no está habilitado.")

        cursor.execute(
            """
            SELECT c.*, f.activa AS finca_activa
            FROM cosechas c
            JOIN fincas f ON f.id = c.finca_id
            WHERE c.id = %s
            FOR UPDATE
            """,
            (cosecha_id,),
        )
        cosecha = cursor.fetchone()

        if (
            not cosecha
            or not cosecha["activa"]
            or not cosecha["finca_activa"]
            or cosecha["cantidad"] <= 0
        ):
            raise ValueError("La cosecha ya no está disponible.")

        if (
            cosecha["precio"] != precio_mostrado
            or cosecha["unidad"] != unidad_mostrada
        ):
            raise ValueError(
                "El precio o la unidad cambió. "
                "Actualiza el catálogo antes de confirmar."
            )

        if cantidad > cosecha["cantidad"]:
            raise ValueError(
                "La cantidad solicitada supera las existencias actuales."
            )

        # NUEVO: evita solicitudes duplicadas. Suma lo que este comprador
        # ya tiene pendiente de esta cosecha y no deja superar el stock.
        cursor.execute(
            """
            SELECT COALESCE(SUM(cantidad), 0) AS pendiente
            FROM pedidos
            WHERE comprador_id = %s
              AND cosecha_id = %s
              AND estado = 'pendiente'
            """,
            (comprador_id, cosecha_id),
        )
        ya_pendiente = cursor.fetchone()["pendiente"]

        if ya_pendiente + cantidad > cosecha["cantidad"]:
            raise ValueError(
                "Ya tienes solicitudes pendientes de este producto y, "
                "sumadas a esta, superan las existencias actuales. "
                "Cancela una solicitud pendiente o reduce la cantidad."
            )

        if (
            cosecha["unidad"] == "unidad"
            and cantidad != cantidad.to_integral_value()
        ):
            raise ValueError("Los productos por unidad requieren cantidades enteras.")

        total = (cantidad * cosecha["precio"]).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        if total <= 0 or total > Decimal("999999999999.99"):
            raise ValueError("El total del pedido está fuera del rango permitido.")

        cursor.execute(
            """
            INSERT INTO pedidos (
                comprador_id,
                cosecha_id,
                cantidad,
                precio_unitario,
                unidad,
                estado
            )
            VALUES (%s, %s, %s, %s, %s, 'pendiente')
            """,
            (
                comprador_id,
                cosecha_id,
                cantidad,
                cosecha["precio"],
                cosecha["unidad"],
            ),
        )
        pedido_id = cursor.lastrowid

    return pedido_id


def listar_pedidos(comprador_id):
    """Consulta únicamente los pedidos del comprador indicado."""
    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            SELECT
                p.id,
                p.creado_en,
                c.producto,
                f.nombre AS finca,
                p.cantidad,
                p.unidad,
                p.precio_unitario,
                ROUND(p.cantidad * p.precio_unitario, 2) AS total,
                p.estado
            FROM pedidos p
            JOIN cosechas c ON c.id = p.cosecha_id
            JOIN fincas f ON f.id = c.finca_id
            WHERE p.comprador_id = %s
            ORDER BY p.creado_en DESC, p.id DESC
            """,
            (comprador_id,),
        )
        return cursor.fetchall()


def cancelar_pedido(comprador_id, pedido_id):
    """
    NUEVO: cancela un pedido pendiente del comprador.
    Como el inventario solo se descuenta cuando el agricultor acepta,
    cancelar un pedido pendiente no requiere devolver existencias.
    """
    with abrir_bd() as (_, cursor):
        cursor.execute("BEGIN PESSIMISTIC")

        cursor.execute(
            """
            SELECT id, estado
            FROM pedidos
            WHERE id = %s AND comprador_id = %s
            FOR UPDATE
            """,
            (pedido_id, comprador_id),
        )
        pedido = cursor.fetchone()

        if pedido is None:
            raise ValueError(
                "El pedido no existe o no pertenece a tu cuenta."
            )

        if pedido["estado"] != "pendiente":
            raise ValueError(
                "Solo puedes cancelar pedidos que siguen pendientes. "
                "Actualiza la vista para ver su estado actual."
            )

        cursor.execute(
            """
            UPDATE pedidos
            SET estado = 'cancelado'
            WHERE id = %s AND comprador_id = %s AND estado = 'pendiente'
            """,
            (pedido_id, comprador_id),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "El pedido cambió de estado. No se pudo cancelar."
            )

    
def registrar_pago(comprador_id, pedido_id):
    """
    Registra un pago simulado y confirmado.
    Solo permite pagar pedidos aceptados.
    """
    with abrir_bd() as (_, cursor):
        cursor.execute("BEGIN PESSIMISTIC")

        # Verificar que el pedido pertenezca al comprador.
        cursor.execute(
            """
            SELECT id, estado, cantidad, precio_unitario
            FROM pedidos
            WHERE id = %s AND comprador_id = %s
            FOR UPDATE
            """,
            (pedido_id, comprador_id),
        )

        pedido = cursor.fetchone()

        if pedido is None:
            raise ValueError(
                "El pedido no existe o no pertenece a tu cuenta."
            )

        if pedido["estado"] != "aceptado":
            raise ValueError(
                "Solo puedes pagar pedidos aceptados por el agricultor."
            )

        # Evitar pagos duplicados.
        cursor.execute(
            """
            SELECT id, estado
            FROM pagos
            WHERE pedido_id = %s
            FOR UPDATE
            """,
            (pedido_id,),
        )

        pago_existente = cursor.fetchone()

        if pago_existente:
            raise ValueError(
                "Este pedido ya tiene un registro de pago."
            )

        # Calcular el monto desde los datos almacenados.
        monto = (
            pedido["cantidad"] * pedido["precio_unitario"]
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if monto <= 0:
            raise ValueError("El monto del pago no es válido.")

        referencia = f"AGRITGO-DEMO-{uuid4().hex[:16].upper()}"

        # Registrar el pago simulado como confirmado.
        cursor.execute(
            """
            INSERT INTO pagos (
                pedido_id,
                monto,
                estado,
                referencia,
                es_simulado
            )
            VALUES (%s, %s, 'confirmado', %s, TRUE)
            """,
            (pedido_id, monto, referencia),
        )

        pago_id = cursor.lastrowid 

    repartir_pago(cursor, pago_id, pedido_id, monto)   


def listar_pagos(comprador_id):
    """Consulta el historial de pagos del comprador."""
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
                c.producto,
                f.nombre AS finca,
                p.cantidad,
                p.unidad
            FROM pagos pa
            JOIN pedidos p ON p.id = pa.pedido_id
            JOIN cosechas c ON c.id = p.cosecha_id
            JOIN fincas f ON f.id = c.finca_id
            WHERE p.comprador_id = %s
            ORDER BY pa.creado_en DESC, pa.id DESC
            """,
            (comprador_id,),
        )

        return cursor.fetchall()