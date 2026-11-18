import streamlit as st
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from html import escape
from pathlib import Path
from mysql.connector import Error as ErrorMySQL

from database.agricultor_db import listar_cosechas
from database.comprador_db import (
    iniciar_comprador,
    crear_pedido,
    listar_pedidos,
    cancelar_pedido,
    registrar_pago,
    listar_pagos
)

# ----------------------------------------------------------------------
# Utilidades comunes
# ----------------------------------------------------------------------
def cop(valor):
    """Formatea un número como pesos colombianos: $1.500.000 COP"""
    signo = "-" if valor < 0 else ""
    return f"{signo}${abs(valor):,.0f} COP".replace(",", ".")


def _normalizar(texto):
    """Minúsculas y sin tildes, para que 'cafe' encuentre 'Café'."""
    texto = unicodedata.normalize("NFD", str(texto).strip().casefold())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


# Vistas del menú lateral
VISTA_INICIO = "🏠 Inicio"
VISTA_FINCAS = "🏡 Fincas"
VISTA_PEDIDOS = "📦 Mis pedidos"

AYUDAS_MENU = {
    VISTA_INICIO: "Explora los productos del campo y solicita tus compras.",
    VISTA_FINCAS: "Consulta los productos de cada finca.",
    VISTA_PEDIDOS: "Revisa tus pedidos, cancela los pendientes y paga los aceptados.",
}

# Estado visual de un pedido: (texto, color de fondo, color de texto)
ESTADOS_PEDIDO = {
    "pendiente": ("Pendiente", "#FFF3CD", "#7A5C00"),
    "por_pagar": ("Aceptado · por pagar", "#DCEBFA", "#1F4E79"),
    "pagado": ("Pagado", "#D4EDDA", "#1E5C34"),
    "rechazado": ("Rechazado", "#F8D7DA", "#8A2C2C"),
    "cancelado": ("Cancelado", "#E2E3E5", "#4A4F54"),
}


# ----------------------------------------------------------------------
# Estilos: misma paleta y tamaños que el módulo del agricultor
# ----------------------------------------------------------------------
ESTILOS = """
<style>
/* FONDO VERDE CLARO */
.stApp {
    background-color: #EAF4E8;
    color: #203D2B;
}

[data-testid="stHeader"] {
    background-color: #EAF4E8;
    color: #203D2B;
}

/* TEXTO GENERAL Y MÉTRICAS LEGIBLES */
[data-testid="stMain"] [data-testid="stMarkdownContainer"],
[data-testid="stMain"] [data-testid="stWidgetLabel"],
[data-testid="stMain"] [data-testid="stMetricLabel"],
[data-testid="stMain"] [data-testid="stMetricValue"] {
    color: #203D2B !important;
}

[data-testid="stMain"] [data-testid="stCaptionContainer"] {
    color: #526B58 !important;
}

/* MENÚ LATERAL VERDE HOJA */
[data-testid="stSidebar"] {
    background-color: #C5DFBA;
    border-right: 1px solid #A4C597;
    color: #203D2B;
}

/* OPCIONES GRANDES Y ESPACIADAS */
[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    font-size: 18px !important;
    font-weight: 600 !important;
    line-height: 1.5 !important;
    color: #203D2B !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 10px 6px !important;
    min-height: 48px !important;
    cursor: pointer;
}

[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 6px !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] > label p {
    font-size: 19px !important;
    font-weight: 700 !important;
}

/* AYUDA EN TONOS VERDES */
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background-color: #E4F0DE !important;
    border: 1px solid #A4C597;
    border-radius: 12px;
}

[data-testid="stSidebar"] [data-testid="stAlert"] p {
    color: #2E5137 !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
}

/* BOTÓN AGRITECHGO */
[class*="st-key-comp_boton_inicio_"] button {
    background-color: #174B35 !important;
    color: #FFFFFF !important;
    border: 1px solid #174B35 !important;
    border-radius: 12px !important;
    min-height: 48px;
}

[class*="st-key-comp_boton_inicio_"] button p {
    color: #FFFFFF !important;
    font-size: 18px !important;
    font-weight: 700 !important;
}

[class*="st-key-comp_boton_inicio_"] button:hover {
    background-color: #236747 !important;
}

/* BOTÓN CERRAR SESIÓN (lo dibuja main.py) */
.st-key-cerrar_sesion button {
    background-color: #A33636 !important;
    color: #FFFFFF !important;
    border: 1px solid #A33636 !important;
    border-radius: 12px !important;
    min-height: 48px;
}

.st-key-cerrar_sesion button p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

.st-key-cerrar_sesion button:hover {
    background-color: #812929 !important;
}

/* MEJORAR LEGIBILIDAD DEL CONTENIDO */
[data-testid="stMain"] p {
    font-size: 17px !important;
    line-height: 1.5 !important;
}

/* TÍTULOS */
[data-testid="stMain"] h1 {
    font-size: 34px !important;
}

[data-testid="stMain"] h2 {
    font-size: 27px !important;
}

[data-testid="stMain"] h3 {
    font-size: 22px !important;
}

/* ETIQUETAS DE FORMULARIOS */
[data-testid="stMain"] [data-testid="stWidgetLabel"] p {
    font-size: 16px !important;
    font-weight: 600 !important;
}

/* TEXTOS SECUNDARIOS */
[data-testid="stMain"] [data-testid="stCaptionContainer"] p {
    font-size: 15px !important;
}

/* FOTOGRAFÍAS UNIFORMES */
[data-testid="stMain"] [data-testid="stImage"] img {
    width: 100% !important;
    height: 260px !important;
    object-fit: cover !important;
    object-position: center !important;
    border-radius: 12px !important;
}

/* ---------- Carrusel horizontal por finca (propio del comprador) ---------- */
.sin-foto {
    background:#EAF3E8; border-radius:12px; height:180px;
    display:flex; align-items:center; justify-content:center;
    flex-direction:column; color:#24543B;
}

.finca-banner {
    background: #236747;
    color: white;
    border-radius: 14px;
    padding: 14px 18px;
    margin-top: 8px;
}
.finca-banner h3 { color: white !important; margin: 0 0 4px 0; }
.finca-banner p  { color: white !important; margin: 2px 0; font-size: 15px !important; opacity: 0.95; }
.finca-banner .hint { font-size: 13px !important; opacity: 0.8; margin-top: 6px; }

div[class*="st-key-carrusel_"] div[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    overflow-x: auto;
    gap: 1rem;
    padding: 8px 4px 14px 4px;
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
}
div[class*="st-key-carrusel_"] div[data-testid="stColumn"],
div[class*="st-key-carrusel_"] div[data-testid="column"] {
    flex: 0 0 260px !important;
    min-width: 260px !important;
    width: 260px !important;
    scroll-snap-align: start;
}
div[class*="st-key-carrusel_"] div[data-testid="stHorizontalBlock"]::-webkit-scrollbar {
    height: 8px;
}
div[class*="st-key-carrusel_"] div[data-testid="stHorizontalBlock"]::-webkit-scrollbar-thumb {
    background: #236747;
    border-radius: 8px;
}
div[class*="st-key-carrusel_"] div[data-testid="stHorizontalBlock"]::-webkit-scrollbar-track {
    background: #C5DFBA;
    border-radius: 8px;
}
div[class*="st-key-carrusel_"] div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #A4C597;
    border-radius: 14px;
}
/* Fotos de las tarjetas del carrusel un poco más bajas que las del agricultor */
div[class*="st-key-carrusel_"] [data-testid="stImage"] img {
    height: 180px !important;
}

/* ---------- Mis pedidos ---------- */
.insignia {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 14px;
    white-space: nowrap;
}
.dato .etiqueta {
    display: block;
    font-size: 12px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #526B58;
}
.dato .valor {
    display: block;
    font-size: 18px;
    font-weight: 700;
    color: #203D2B;
}
/* Confirmar cancelación en rojo, igual que Cerrar sesión */
[class*="st-key-comp_confirmar_cancelar_"] button {
    background-color: #A33636 !important;
    color: #FFFFFF !important;
    border: 1px solid #A33636 !important;
    border-radius: 12px !important;
}
[class*="st-key-comp_confirmar_cancelar_"] button p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
[class*="st-key-comp_confirmar_cancelar_"] button:hover {
    background-color: #812929 !important;
}
</style>
"""


# ----------------------------------------------------------------------
# Componentes visuales
# ----------------------------------------------------------------------

def _solicitar_pedido(comprador_id, cosecha_id, precio, unidad, clave):
    """
    Callback del botón "Solicitar compra".
    Crea el pedido y deja la cantidad en cero para que la misma
    solicitud no se pueda enviar dos veces por accidente.
    """
    cantidad = round(float(st.session_state.get(f"comp_cantidad_{clave}", 0.0)), 3)
    mensaje_key = f"comp_msg_{clave}"

    try:
        pedido_id = crear_pedido(
            comprador_id,
            cosecha_id,
            cantidad,
            precio,
            unidad,
        )
    except ValueError as error:
        st.session_state[mensaje_key] = ("error", str(error))
    except ErrorMySQL as error:
        st.session_state[mensaje_key] = (
            "error",
            "No se pudo confirmar el resultado del pedido. "
            "Actualiza Mis pedidos antes de volver a intentarlo. "
            f"Código: {error.errno}.",
        )
    except ConnectionError:
        st.session_state[mensaje_key] = ("error", "No se pudo conectar con TiDB.")
    else:
        st.session_state[mensaje_key] = (
            "ok",
            f"Pedido #{pedido_id} guardado. "
            "Está pendiente de aceptación del agricultor. "
            "Puedes verlo o cancelarlo en Mis pedidos.",
        )
        st.session_state[f"comp_cantidad_{clave}"] = 0.0
        st.toast(f"Pedido #{pedido_id} enviado al agricultor", icon="✅")


def _tarjeta_producto(cosecha, comprador_id):
    unidad = cosecha["unidad"]
    precio = cosecha["precio"]
    disponible = cosecha["cantidad"]
    clave = f"{comprador_id}_{cosecha['id']}"

    with st.container(border=True):
        if cosecha.get("foto"):
            st.image(cosecha["foto"], use_container_width=True)
        else:
            st.markdown(
                """
                <div class="sin-foto">
                    <div style="font-size:40px;">🌱</div>
                    <b>Sin fotografía</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(f"**{cosecha['producto']}**")
        st.caption(
            f"{cop(precio)} por {unidad} · "
            f"{disponible:g} {unidad} disp."
        )
        st.caption(f"⭐ {cosecha['calidad']}")

        # Resultado de la última solicitud de esta tarjeta (si existe)
        mensaje = st.session_state.pop(f"comp_msg_{clave}", None)

        with st.expander("🛒 Comprar", expanded=mensaje is not None):

            cantidad = st.number_input(
                f"Cantidad en {unidad}",
                min_value=0.0,
                max_value=float(disponible),
                value=0.0,
                step=1.0 if unidad == "unidad" else 0.1,
                format="%.3f",
                key=f"comp_cantidad_{clave}",
            )

            total = (
                Decimal(str(cantidad)) * precio
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            st.markdown(f"**Total:** {cop(total)}")
            st.caption(
                "Tu solicitud queda pendiente hasta que el agricultor la "
                "acepte. El inventario se descuenta en ese momento y solo "
                "entonces podrás pagar."
            )

            st.button(
                "✅ Solicitar compra",
                key=f"comp_solicitar_{clave}",
                on_click=_solicitar_pedido,
                args=(comprador_id, cosecha["id"], precio, unidad, clave),
                disabled=cantidad <= 0,
                use_container_width=True,
            )

            if mensaje:
                tipo, texto_mensaje = mensaje
                if tipo == "ok":
                    st.success(texto_mensaje)
                else:
                    st.error(texto_mensaje)



def _banner_finca(nombre, lotes):
    productos = ", ".join(
        sorted({lote["producto"] for lote in lotes})
    )

    ubicacion = " · ".join(
        parte
        for parte in (
            lotes[0].get("municipio"),
            lotes[0].get("vereda"),
        )
        if parte
    ) or "Ubicación sin registrar"

    pista = (
        '<p class="hint">Desliza para ver más productos ➜</p>'
        if len(lotes) > 1
        else ""
    )

    st.markdown(
        f"""
        <div class="finca-banner">
            <h3>🏡 {escape(nombre)}</h3>
            <p>📍 {escape(ubicacion)} · 📦 {len(lotes)} producto(s)</p>
            <p>🌾 {escape(productos)}</p>
            {pista}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _fila_finca(finca_id, lotes, comprador_id):
    _banner_finca(lotes[0]["finca"], lotes)

    with st.container(
        key=f"carrusel_{comprador_id}_{finca_id}"
    ):
        columnas = st.columns(len(lotes))

        for columna, lote in zip(columnas, lotes):
            with columna:
                _tarjeta_producto(lote, comprador_id)

    st.divider()


def _agrupar_fincas(cosechas):
    fincas = {}

    for cosecha in cosechas:
        fincas.setdefault(cosecha["finca_id"], []).append(cosecha)

    return fincas


# ----------------------------------------------------------------------
# Vistas
# ----------------------------------------------------------------------

def _barra_busqueda(comprador_id):
    _, centro, _ = st.columns([1, 3, 1])

    with centro:
        c_input, c_btn = st.columns([5, 1])

        busqueda = c_input.text_input(
            "Buscar",
            placeholder="Producto o finca: Café, Yuca, Finca El Mirador...",
            label_visibility="collapsed",
            key=f"comp_busqueda_{comprador_id}",
        )

        c_btn.button(
            "Buscar",
            use_container_width=True,
            key=f"comp_buscar_{comprador_id}",
        )

    return _normalizar(busqueda)


def _vista_inicio(comprador_id, cosechas):
    st.subheader("🌾 Productos del campo")
    st.write("Busca por producto o finca y desliza para ver todos los lotes.")

    busqueda = _barra_busqueda(comprador_id)

    if busqueda:
        cosechas = [
            cosecha
            for cosecha in cosechas
            if busqueda in _normalizar(cosecha["producto"])
            or busqueda in _normalizar(cosecha["finca"])
        ]

    if not cosechas:
        st.info(
            "No hay cosechas disponibles que coincidan en este momento."
        )
        return

    for finca_id, lotes in _agrupar_fincas(cosechas).items():
        _fila_finca(finca_id, lotes, comprador_id)


def _vista_fincas(comprador_id, cosechas):
    st.subheader("🏡 Fincas")
    st.write("Selecciona una finca para ver todos sus productos.")

    fincas = _agrupar_fincas(cosechas)

    if not fincas:
        st.info("Aún no hay fincas con cosechas disponibles.")
        return

    elegida = st.selectbox(
        "Selecciona una finca",
        options=list(fincas),
        format_func=lambda finca_id: (
            f"{fincas[finca_id][0]['finca']} · Finca #{finca_id}"
        ),
        key=f"comp_finca_{comprador_id}",
    )

    _fila_finca(elegida, fincas[elegida], comprador_id)


# ----------------------------------------------------------------------
# Mis pedidos
# ----------------------------------------------------------------------

def _estado_visual(pedido, pedidos_pagados):
    """Convierte el estado de la BD en el estado que ve el comprador."""
    estado = pedido["estado"]

    if estado == "aceptado":
        return "pagado" if pedido["id"] in pedidos_pagados else "por_pagar"

    return estado


def _insignia(clave_estado):
    etiqueta, fondo, color = ESTADOS_PEDIDO.get(
        clave_estado,
        (str(clave_estado).capitalize(), "#E2E3E5", "#4A4F54"),
    )
    return (
        f'<span class="insignia" style="background:{fondo};color:{color};">'
        f"{escape(etiqueta)}</span>"
    )


def _dato(etiqueta, valor):
    return (
        '<div class="dato">'
        f'<span class="etiqueta">{escape(etiqueta)}</span>'
        f'<span class="valor">{escape(str(valor))}</span>'
        "</div>"
    )


def _tarjeta_pedido(comprador_id, pedido, clave_estado):
    with st.container(border=True):
        col_titulo, col_estado = st.columns(
            [3, 2], vertical_alignment="center"
        )
        col_titulo.markdown(f"### 📦 Pedido #{pedido['id']}")
        col_estado.markdown(
            f'<div style="text-align:right;">{_insignia(clave_estado)}</div>',
            unsafe_allow_html=True,
        )

        fecha = (
            pedido["creado_en"].strftime("%d/%m/%Y %H:%M")
            if pedido.get("creado_en")
            else "—"
        )
        st.caption(f"🏡 {pedido['finca']} · 📅 {fecha}")

        d1, d2, d3, d4 = st.columns([2, 1.2, 1.5, 1.5])
        d1.markdown(_dato("Producto", pedido["producto"]), unsafe_allow_html=True)
        d2.markdown(
            _dato("Cantidad", f"{pedido['cantidad']:g} {pedido['unidad']}"),
            unsafe_allow_html=True,
        )
        d3.markdown(
            _dato("Precio unitario", cop(pedido["precio_unitario"])),
            unsafe_allow_html=True,
        )
        d4.markdown(
            _dato("Total", cop(pedido["total"])),
            unsafe_allow_html=True,
        )

        st.markdown("")
        col_mensaje, col_accion = st.columns([2, 1], vertical_alignment="center")

        if clave_estado == "pendiente":
            col_mensaje.caption(
                "Esperando respuesta del agricultor. "
                "Puedes cancelar la solicitud mientras siga pendiente."
            )

            with col_accion:
                with st.popover("Cancelar pedido", use_container_width=True):
                    st.write(
                        f"¿Seguro que deseas cancelar el pedido "
                        f"#{pedido['id']}?"
                    )
                    st.caption("Esta acción no se puede deshacer.")

                    if st.button(
                        "Sí, cancelar pedido",
                        key=f"comp_confirmar_cancelar_{comprador_id}_{pedido['id']}",
                        use_container_width=True,
                    ):
                        try:
                            cancelar_pedido(comprador_id, pedido["id"])
                        except ValueError as error:
                            st.error(str(error))
                        except ErrorMySQL as error:
                            st.error(
                                "No se pudo cancelar el pedido. "
                                f"Código: {error.errno}."
                            )
                        except ConnectionError:
                            st.error("No se pudo conectar con TiDB.")
                        else:
                            st.session_state[
                                f"comp_aviso_{comprador_id}"
                            ] = f"Pedido #{pedido['id']} cancelado correctamente."
                            st.rerun()

        elif clave_estado == "por_pagar":
            col_mensaje.caption(
                "El agricultor aceptó tu pedido. Ya puedes realizar el pago."
            )

            with col_accion:
                if st.button(
                    "💳 Pagar pedido",
                    key=f"comp_pagar_{comprador_id}_{pedido['id']}",
                    use_container_width=True,
                ):
                    try:
                        pago_id = registrar_pago(
                            comprador_id,
                            pedido["id"],
                        )
                    except ValueError as error:
                        st.error(str(error))
                    except ErrorMySQL as error:
                        st.error(
                            f"No se pudo registrar el pago. "
                            f"Código: {error.errno}."
                        )
                    except ConnectionError:
                        st.error("No se pudo conectar con TiDB.")
                    else:
                        st.session_state[
                            f"comp_aviso_{comprador_id}"
                        ] = (
                            f"Pago simulado #{pago_id} "
                            "registrado correctamente."
                        )
                        st.rerun()

        elif clave_estado == "pagado":
            col_mensaje.caption("✅ Pedido pagado. Consulta el detalle en el historial de pagos.")

        elif clave_estado == "rechazado":
            col_mensaje.caption("El agricultor no pudo atender este pedido.")

        elif clave_estado == "cancelado":
            col_mensaje.caption("Cancelaste este pedido.")


def _vista_pedidos(comprador_id):
    st.subheader("📦 Mis pedidos")
    st.write(
        "Consulta el estado de tus solicitudes, cancela las pendientes "
        "y paga las que el agricultor aceptó."
    )

    pedidos = listar_pedidos(comprador_id)
    pagos = listar_pagos(comprador_id)
    pedidos_pagados = {pago["pedido_id"] for pago in pagos}

    claves = [_estado_visual(p, pedidos_pagados) for p in pedidos]

    m1, m2, m3 = st.columns(3)
    m1.metric("Pendientes", claves.count("pendiente"))
    m2.metric("Por pagar", claves.count("por_pagar"))
    m3.metric("Pagados", claves.count("pagado"))

    st.markdown("---")

    if not pedidos:
        st.info("Aún no tienes pedidos. Elige un producto en Inicio.")
    else:
        col_filtro, _ = st.columns([1, 2])
        filtro = col_filtro.selectbox(
            "Filtrar por estado",
            ["Todos"] + [datos[0] for datos in ESTADOS_PEDIDO.values()],
            key=f"comp_filtro_{comprador_id}",
        )

        visibles = [
            (pedido, clave)
            for pedido, clave in zip(pedidos, claves)
            if filtro == "Todos"
            or ESTADOS_PEDIDO.get(clave, (clave,))[0] == filtro
        ]

        st.caption(f"Mostrando {len(visibles)} de {len(pedidos)} pedidos")

        if not visibles:
            st.info("No tienes pedidos con ese estado.")

        for pedido, clave in visibles:
            _tarjeta_pedido(comprador_id, pedido, clave)

    st.markdown("---")
    st.subheader("💰 Historial de pagos")

    if not pagos:
        st.info("Todavía no tienes pagos registrados.")
        return

    filas = []

    for pago in pagos:
        filas.append({
            "Pago": pago["pago_id"],
            "Pedido": pago["pedido_id"],
            "Producto": pago["producto"],
            "Finca": pago["finca"],
            "Monto": cop(pago["monto"]),
            "Referencia": pago["referencia"],
            "Estado": pago["estado"].capitalize(),
            "Tipo": "Simulado" if pago["es_simulado"] else "Real",
        })

    st.dataframe(
        filas,
        use_container_width=True,
        hide_index=True,
    )



# ----------------------------------------------------------------------
# Punto de entrada
# ----------------------------------------------------------------------

def ejecutar_modo_comprador():

    st.markdown(ESTILOS, unsafe_allow_html=True)

    usuario = str(st.session_state.get("usuario", "")).strip()

    if not usuario:
        st.error("Ingresa primero con un usuario.")
        return

    try:
        comprador_id = iniciar_comprador(usuario)
    except ValueError as error:
        st.error(str(error))
        return
    except (ErrorMySQL, ConnectionError):
        st.error("No se pudo cargar el comprador desde TiDB.")
        return

    try:
        cosechas = listar_cosechas(solo_disponibles=True)
    except (ErrorMySQL, ConnectionError):
        st.error("No se pudo cargar el catálogo desde TiDB.")
        return

    # ------------------------------------------------------------------
    # Encabezado (mismo bloque visual del agricultor)
    # ------------------------------------------------------------------
    st.markdown(
        f"""
        <div style="
            background:#174B35;
            padding:28px;
            border-radius:18px;
            margin-bottom:20px;
        ">
            <div style="color:#D5E8B8;font-size:15px;">
                AGRITECHGO · COMPRADOR
            </div>
            <div style="
                color:#FFFFFF;
                font-size:34px;
                font-weight:750;
                margin:8px 0;
            ">
                AgritechGO
            </div>
            <div style="color:#FFFFFF;font-size:17px;">
                Bienvenido, {escape(usuario)}.
                Compra alimentos frescos directamente a los
                agricultores de la región.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Tus pedidos se guardan en TiDB Cloud. "
        "La información se consulta al cargar o actualizar la vista."
    )

    if st.button(
        "🔄 Actualizar información",
        key=f"comp_actualizar_{comprador_id}",
    ):
        st.rerun()

    mensaje = st.session_state.pop(
        f"comp_aviso_{comprador_id}",
        "",
    )
    if mensaje:
        st.success(mensaje)

    col1, col2, col3 = st.columns(3)
    col1.metric("Productos disponibles", len(cosechas))
    col2.metric("Fincas con cosecha", len(_agrupar_fincas(cosechas)))
    col3.metric("Intermediarios", 0)

    st.markdown("---")

    # ------------------------------------------------------------------
    # Menú lateral: logo + botón AgritechGO + navegación
    # ------------------------------------------------------------------
    menu_key = f"comp_vista_{comprador_id}"

    # Se ejecuta antes de volver a dibujar el menú.
    def volver_al_inicio():
        st.session_state[menu_key] = VISTA_INICIO

    logo_path = Path(__file__).resolve().parent.parent / "logo.png"

    with st.sidebar:
        col_logo, col_nombre = st.columns(
            [1, 3],
            gap="small",
            vertical_alignment="center",
        )
        with col_logo:
            if logo_path.is_file():
                st.image(str(logo_path), width=60)

        with col_nombre:
            st.button(
                "AgritechGO",
                key=f"comp_boton_inicio_{comprador_id}",
                help="Volver a Inicio",
                on_click=volver_al_inicio,
                use_container_width=True,
            )

    vista = st.sidebar.radio(
        "Navegación:",
        [VISTA_INICIO, VISTA_FINCAS, VISTA_PEDIDOS],
        key=menu_key,
    )

    st.sidebar.markdown("---")
    st.sidebar.info(AYUDAS_MENU[vista])

    # ------------------------------------------------------------------
    # Contenido según la sección
    # ------------------------------------------------------------------
    if vista == VISTA_INICIO:
        _vista_inicio(comprador_id, cosechas)
    elif vista == VISTA_FINCAS:
        _vista_fincas(comprador_id, cosechas)
    else:
        _vista_pedidos(comprador_id)


# --- BLOQUE PARA PRUEBAS DIRECTAS ---
if __name__ == "__main__":
    if "usuario" not in st.session_state:
        st.session_state.usuario = "Luis Comprador (Prueba)"
    if "agri_datos" not in st.session_state:
        st.session_state.agri_datos = {
            "agricultor_juan": {
                "cosechas": [
                    {"id": "1", "producto": "Café Especial Caturra", "finca": "Finca Juan",
                     "precio": 85000, "unidad": "kg", "cantidad": 50,
                     "calidad": "Premium", "activa": True, "foto": None},
                    {"id": "2", "producto": "Pollo", "finca": "Finca Juan",
                     "precio": 12000, "unidad": "kg", "cantidad": 30,
                     "calidad": "Fresco", "activa": True, "foto": None},
                ]
            },
            "agricultor_andres": {
                "cosechas": [
                    {"id": "3", "producto": "Arroz", "finca": "Finca Andrés",
                     "precio": 4500, "unidad": "kg", "cantidad": 200,
                     "calidad": "Estándar", "activa": True, "foto": None},
                    {"id": "4", "producto": "Maíz", "finca": "Finca Andrés",
                     "precio": 3000, "unidad": "kg", "cantidad": 120,
                     "calidad": "Estándar", "activa": True, "foto": None},
                ]
            },
        }

    ejecutar_modo_comprador() 
    
# Para probar solo esta parte:  py -m streamlit run modos/comprador.py
# Para probar todo el proyecto: py -m streamlit run main.py