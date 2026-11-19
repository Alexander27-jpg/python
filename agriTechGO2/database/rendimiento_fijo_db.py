from decimal import Decimal, ROUND_HALF_UP

from database.agricultor_db import abrir_bd

CENTAVO = Decimal("0.01")


def calcular_ganancia(monto, rentabilidad):
    """
    rentabilidad es una fracción:
    0.12 equivale al 12 %.
    """
    return (Decimal(str(monto)) * Decimal(str(rentabilidad))).quantize(
        CENTAVO, rounding=ROUND_HALF_UP
    )


def listar_ganancias_inversionista(usuario_id):
    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            SELECT
                g.inversion_id,
                g.proyecto_id,
                p.titulo AS proyecto,
                f.nombre AS finca,
                g.monto,
                g.creado_en AS fecha
            FROM ganancias_inversiones g
            JOIN proyectos p ON p.id = g.proyecto_id
            JOIN fincas f ON f.id = p.finca_id
            WHERE g.inversionista_id = %s
            ORDER BY g.creado_en DESC, g.id DESC
            """,
            (usuario_id,),
        )
        return cursor.fetchall()


def finalizar_proyecto(agricultor_id, proyecto_id):
    """
    Finaliza un proyecto financiado y acredita
    una sola vez la rentabilidad de cada inversión.

    Toda la operación usa una única transacción.
    """

    with abrir_bd() as (_, cursor):
        cursor.execute("BEGIN PESSIMISTIC")

        cursor.execute(
            """
            SELECT
                p.id, p.estado, p.meta,
                f.agricultor_id
            FROM proyectos p
            JOIN fincas f ON f.id = p.finca_id
            WHERE p.id = %s
            FOR UPDATE
            """,
            (proyecto_id,),
        )
        proyecto = cursor.fetchone()

        if not proyecto:
            raise ValueError("El proyecto no existe.")

        if proyecto["agricultor_id"] != agricultor_id:
            raise ValueError("El proyecto no te pertenece.")

        if proyecto["estado"] != "financiado":
            raise ValueError(
                "Solo se pueden finalizar proyectos "
                "completamente financiados y pendientes "
                "de liquidación."
            )

        cursor.execute(
            """
            SELECT
                id, inversionista_id, monto,
                rentabilidad_estimada
            FROM inversiones
            WHERE proyecto_id = %s
              AND estado = 'activa'
              AND es_simulada = TRUE
            FOR UPDATE
            """,
            (proyecto_id,),
        )
        inversiones = cursor.fetchall()

        if not inversiones:
            raise ValueError("No existen inversiones activas para liquidar.")

        total_aportado = sum(
            (Decimal(str(i["monto"])) for i in inversiones),
            Decimal("0.00"),
        )

        if total_aportado < Decimal(str(proyecto["meta"])):
            raise ValueError("El proyecto todavía no tiene " "financiación completa.")

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM ganancias_inversiones
            WHERE proyecto_id = %s
            """,
            (proyecto_id,),
        )

        if cursor.fetchone()["total"] > 0:
            raise ValueError(
                "Este proyecto ya tiene liquidaciones "
                "registradas. Revisa antes de continuar."
            )

        total_ganancias = Decimal("0.00")

        for inversion in inversiones:
            ganancia = calcular_ganancia(
                inversion["monto"],
                inversion["rentabilidad_estimada"],
            )

            usuario_id = inversion["inversionista_id"]
            inversion_id = inversion["id"]

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
                raise ValueError(f"Wallet inválida para el usuario {usuario_id}.")

            nuevo_saldo = Decimal(str(wallet["saldo"])) + ganancia

            if nuevo_saldo > Decimal("999999999999.99"):
                raise ValueError("El saldo supera el límite permitido.")

            cursor.execute(
                """
                INSERT INTO ganancias_inversiones
                    (inversion_id, inversionista_id,
                     proyecto_id, monto)
                VALUES (%s, %s, %s, %s)
                """,
                (inversion_id, usuario_id, proyecto_id, ganancia),
            )

            if ganancia > 0:
                cursor.execute(
                    """
                    UPDATE wallets
                    SET saldo = saldo + %s
                    WHERE usuario_id = %s
                      AND es_simulada = TRUE
                    """,
                    (ganancia, usuario_id),
                )

                if cursor.rowcount != 1:
                    raise ValueError("No se pudo acreditar la ganancia.")

                cursor.execute(
                    """
                    INSERT INTO movimientos_wallet
                        (usuario_id, inversion_id,
                         tipo, monto, detalle)
                    VALUES (%s, %s, 'rendimiento', %s, %s)
                    """,
                    (
                        usuario_id,
                        inversion_id,
                        ganancia,
                        f"Rentabilidad final del proyecto #{proyecto_id}",
                    ),
                )

            total_ganancias += ganancia

        cursor.execute(
            """
            UPDATE inversiones
            SET estado = 'finalizada'
            WHERE proyecto_id = %s
              AND estado = 'activa'
            """,
            (proyecto_id,),
        )

        cursor.execute(
            """
            UPDATE proyectos
            SET estado = 'cerrado'
            WHERE id = %s
              AND estado = 'financiado'
            """,
            (proyecto_id,),
        )

        if cursor.rowcount != 1:
            raise ValueError("No se pudo cerrar el proyecto.")

        return total_ganancias
