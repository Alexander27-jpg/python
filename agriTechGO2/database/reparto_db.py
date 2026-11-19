from decimal import Decimal, ROUND_DOWN

# El agricultor nunca cede mas de este porcentaje de una venta, aunque sume
# varios proyectos con porcentaje en la misma finca.
TOPE_PORCENTAJE = Decimal("50")
CENTAVO = Decimal("0.01")
TIPO_MOVIMIENTO = "rendimiento"  # ADAPTAR: si 'tipo' es un ENUM, agregar este valor


def _dec(valor):
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def _col(fila, indice, nombre):
    """Lee una columna sin importar si el cursor devuelve tuplas o diccionarios."""
    return fila[nombre] if isinstance(fila, dict) else fila[indice]


# ----------------------------------------------------------------------
# 1) Calculo puro (sin base de datos, facil de probar)
# ----------------------------------------------------------------------
def calcular_repartos(monto_pago, proyectos):
    """
    monto_pago: total pagado por el comprador.
    proyectos: lista de dicts
        {"proyecto_id": 1, "porcentaje": 10, "aportes": [(inversionista_id, monto), ...]}
    Devuelve una lista de tuplas (proyecto_id, inversionista_id, monto).

    Reglas:
    - Solo participan proyectos con porcentaje > 0 y con aportes.
    - Si la suma de porcentajes supera TOPE_PORCENTAJE, se reduce cada uno
      proporcionalmente para que el total ceda a lo sumo ese tope.
    - Dentro de un proyecto se reparte en proporcion a lo aportado.
    - Se redondea hacia abajo al centavo; el sobrante va al mayor aportante,
      asi la suma del proyecto siempre cuadra exacto.
    """
    monto = _dec(monto_pago)
    elegibles = []
    for proyecto in proyectos:
        porcentaje = _dec(proyecto["porcentaje"])
        aportes = [(i, _dec(m)) for i, m in proyecto["aportes"] if _dec(m) > 0]
        if porcentaje > 0 and aportes:
            elegibles.append((proyecto["proyecto_id"], porcentaje, aportes))

    if monto <= 0 or not elegibles:
        return []

    suma = sum(p for _, p, _ in elegibles)
    factor = TOPE_PORCENTAJE / suma if suma > TOPE_PORCENTAJE else Decimal("1")

    resultado = []
    for proyecto_id, porcentaje, aportes in elegibles:
        fondo = (monto * porcentaje * factor / 100).quantize(CENTAVO, ROUND_DOWN)
        total_aportes = sum(m for _, m in aportes)

        partes = [
            [i, (fondo * m / total_aportes).quantize(CENTAVO, ROUND_DOWN)]
            for i, m in aportes
        ]
        sobrante = fondo - sum(parte[1] for parte in partes)
        mayor = max(range(len(aportes)), key=lambda k: aportes[k][1])
        partes[mayor][1] += sobrante

        for inversionista_id, parte in partes:
            if parte > 0:
                resultado.append((proyecto_id, inversionista_id, parte))
    return resultado


# ----------------------------------------------------------------------
# 2) Operacion dentro de la transaccion del pago
# ----------------------------------------------------------------------
def _acreditar_wallet(cursor, inversionista_id, monto, detalle):
    # ADAPTAR: nombres de tablas/columnas de la wallet. Si tu saldo se calcula
    # sumando movimientos (sin columna 'saldo'), borra el UPDATE y deja el INSERT.
    cursor.execute(
        "UPDATE wallets SET saldo = saldo + %s WHERE usuario_id = %s",
        (monto, inversionista_id),
    )
    if cursor.rowcount == 0:
        raise ValueError("No se encontro la wallet del inversionista.")
    cursor.execute(
        "INSERT INTO movimientos_wallet (usuario_id, tipo, monto, detalle) "
        "VALUES (%s, %s, %s, %s)",
        (inversionista_id, TIPO_MOVIMIENTO, monto, detalle),
    )


def repartir_pago(cursor, pago_id, pedido_id, monto_pago):
    """
    LLAMAR DENTRO de registrar_pago, despues de insertar el pago y ANTES del
    commit, con el mismo cursor. Si algo falla, el rollback deshace todo.
    Devuelve el total repartido (Decimal).
    """
    # No repartir dos veces el mismo pago
    cursor.execute(       
       "SELECT COUNT(*) AS total FROM repartos_inversionistas WHERE pago_id = %s",
        (pago_id,),
    )
    if _col(cursor.fetchone(), 0, "total") > 0:
        return Decimal("0.00")

    # Finca del pedido: pedido -> cosecha -> finca   (ADAPTAR nombres)
    cursor.execute(
        "SELECT co.finca_id FROM pedidos pe "
        "JOIN cosechas co ON co.id = pe.cosecha_id WHERE pe.id = %s",
        (pedido_id,),
    )
    fila = cursor.fetchone()
    if not fila:
        raise ValueError("No se encontro la finca del pedido.")
    finca_id = _col(fila, 0, "finca_id")

    # Proyectos de esa finca con porcentaje, y lo aportado por cada inversionista
    # (ADAPTAR: 'inversionista_id' puede llamarse 'usuario_id' en tu tabla)
    cursor.execute(
        """
        SELECT
            pr.id AS proyecto_id,
            pr.porcentaje_ventas AS porcentaje_ventas,
            iv.inversionista_id AS inversionista_id,
            SUM(iv.monto) AS total_aportado
        FROM proyectos pr
        JOIN inversiones iv ON iv.proyecto_id = pr.id
        WHERE pr.finca_id = %s
          AND pr.es_simulado = TRUE
          AND pr.porcentaje_ventas > 0
          AND iv.estado IN ('activa', 'finalizada')
          AND iv.es_simulada = TRUE
        GROUP BY
            pr.id,
            pr.porcentaje_ventas,
            iv.inversionista_id
        ORDER BY pr.id, iv.inversionista_id
        """,
        (finca_id,),
    )

    filas = cursor.fetchall()

    agrupados = {}

    for fila in filas:
        proyecto_id = _col(fila, 0, "proyecto_id")

        entrada = agrupados.setdefault(
            proyecto_id,
            {
                "proyecto_id": proyecto_id,
                "porcentaje": _col(fila, 1, "porcentaje_ventas"),
                "aportes": [],
            },
        )

        entrada["aportes"].append(
            (
                _col(fila, 2, "inversionista_id"),
                _col(fila, 3, "total_aportado"),
            )
        )

    repartos = calcular_repartos(monto_pago, list(agrupados.values()))

    total = Decimal("0.00")
    for proyecto_id, inversionista_id, monto in repartos:
        cursor.execute(
            "INSERT INTO repartos_inversionistas "
            "(pago_id, proyecto_id, inversionista_id, monto) VALUES (%s, %s, %s, %s)",
            (pago_id, proyecto_id, inversionista_id, monto),
        )
        _acreditar_wallet(
            cursor,
            inversionista_id,
            monto,
            f"Rendimiento por venta (pago #{pago_id}, proyecto #{proyecto_id})",
        )
        total += monto
    return total


# ----------------------------------------------------------------------
# 3) Consultas para la interfaz (abren su propia conexion)
# ----------------------------------------------------------------------
def total_rendimientos(inversionista_id):
    from database.agricultor_db import abrir_bd

    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            SELECT COALESCE(SUM(monto), 0) AS total
            FROM repartos_inversionistas
            WHERE inversionista_id = %s
            """,
            (inversionista_id,),
        )
        return _dec(_col(cursor.fetchone(), 0, "total"))


def repartido_por_pago(pago_ids):
    from database.agricultor_db import abrir_bd

    pago_ids = list(pago_ids)
    if not pago_ids:
        return {}

    marcas = ",".join(["%s"] * len(pago_ids))

    with abrir_bd() as (_, cursor):
        cursor.execute(
            f"""
            SELECT pago_id, SUM(monto) AS total
            FROM repartos_inversionistas
            WHERE pago_id IN ({marcas})
            GROUP BY pago_id
            """,
            tuple(pago_ids),
        )

        return {
            _col(f, 0, "pago_id"): _dec(_col(f, 1, "total"))
            for f in cursor.fetchall()
        }


def porcentajes_por_proyecto(proyecto_ids):
    from database.agricultor_db import abrir_bd

    proyecto_ids = list(proyecto_ids)
    if not proyecto_ids:
        return {}

    marcas = ",".join(["%s"] * len(proyecto_ids))

    with abrir_bd() as (_, cursor):
        cursor.execute(
            f"""
            SELECT id, porcentaje_ventas
            FROM proyectos
            WHERE id IN ({marcas})
            """,
            tuple(proyecto_ids),
        )

        return {
            _col(f, 0, "id"): _dec(_col(f, 1, "porcentaje_ventas"))
            for f in cursor.fetchall()
        }


def listar_repartos_inversionista(inversionista_id, limite=50):
    from database.agricultor_db import abrir_bd

    limite = max(1, min(int(limite), 500))

    with abrir_bd() as (_, cursor):
        cursor.execute(
            """
            SELECT
                ri.creado_en AS fecha,
                f.nombre AS finca,
                pr.titulo AS proyecto,
                co.producto AS producto,
                ri.pago_id AS pago_id,
                ri.monto AS monto
            FROM repartos_inversionistas ri
            JOIN proyectos pr ON pr.id = ri.proyecto_id
            JOIN fincas f ON f.id = pr.finca_id
            JOIN pagos pa ON pa.id = ri.pago_id
            JOIN pedidos pe ON pe.id = pa.pedido_id
            JOIN cosechas co ON co.id = pe.cosecha_id
            WHERE ri.inversionista_id = %s
            ORDER BY ri.creado_en DESC, ri.id DESC
            LIMIT %s
            """,
            (inversionista_id, limite),
        )

        return [
            {
                "fecha": _col(f, 0, "fecha"),
                "finca": _col(f, 1, "finca"),
                "proyecto": _col(f, 2, "proyecto"),
                "producto": _col(f, 3, "producto"),
                "pago_id": _col(f, 4, "pago_id"),
                "monto": _dec(_col(f, 5, "monto")),
            }
            for f in cursor.fetchall()
        ]