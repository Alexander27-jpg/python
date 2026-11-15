import streamlit as st
from decimal import Decimal, ROUND_HALF_UP
from html import escape
from mysql.connector import Error as ErrorMySQL

from database.agricultor_db import listar_cosechas
from database.comprador_db import (
    iniciar_comprador,
    crear_pedido,
    listar_pedidos,
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





# ----------------------------------------------------------------------
# Estilos (barra de búsqueda, panel azul de finca)
# ----------------------------------------------------------------------
ESTILOS = """
<style>
.finca-panel {
    background: #4068A8;
    color: white;
    border-radius: 10px;
    padding: 18px;
    min-height: 260px;
}
.finca-panel h3 { color: white; margin: 0 0 8px 0; }
.finca-panel p  { margin: 4px 0; font-size: 0.95rem; }
.sin-foto {
    background:#EAF3E8; border-radius:8px; height:140px;
    display:flex; align-items:center; justify-content:center; color:#24543B;
}

/* ---------- Carrusel horizontal por finca ---------- */
.finca-banner {
    background: #4068A8;
    color: white;
    border-radius: 10px;
    padding: 14px 18px;
    margin-top: 8px;
}
.finca-banner h3 { color: white; margin: 0 0 4px 0; }
.finca-banner p  { margin: 2px 0; font-size: 0.9rem; opacity: 0.95; }
.finca-banner .hint { font-size: 0.8rem; opacity: 0.8; margin-top: 6px; }

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
    background: #4068A8;
    border-radius: 8px;
}
div[class*="st-key-carrusel_"] div[data-testid="stHorizontalBlock"]::-webkit-scrollbar-track {
    background: #E3EAF5;
    border-radius: 8px;
}
</style>
"""





# ----------------------------------------------------------------------
# Componentes visuales
# ----------------------------------------------------------------------

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
                '<div class="sin-foto"><b>🌱 Cosecha Local</b></div>',
                unsafe_allow_html=True,
            )

        st.markdown(f"**{cosecha['producto']}**")
        st.caption(
            f"{cop(precio)} por {unidad} · "
            f"{disponible:g} {unidad} disp."
        )
        st.caption(f"⭐ {cosecha['calidad']}")

        with st.expander("🛒 Comprar"):

            cantidad = st.number_input(
                f"Cantidad en {unidad}",
                min_value=0.0,
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
                "El pedido queda pendiente de aceptación. "
                "No se cobra ni se reserva inventario todavía."
            )

            if st.button(
                "✅ Solicitar compra",
                key=f"comp_solicitar_{clave}",
            ):
                try:
                    pedido_id = crear_pedido(
                        comprador_id,
                        cosecha["id"],
                        cantidad,
                        precio,
                        unidad,
                    )
                except ValueError as error:
                    st.error(str(error))
                except ErrorMySQL as error:
                    st.error(
                        "No se pudo confirmar el resultado del pedido. "
                        "Actualiza Mis pedidos antes de volver a intentarlo. "
                        f"Código: {error.errno}."
                    )
                except ConnectionError:
                    st.error("No se pudo conectar con TiDB.")
                else:
                    st.session_state[
                        f"comp_aviso_{comprador_id}"
                    ] = (
                        f"Pedido #{pedido_id} guardado. "
                        "Está pendiente de aceptación del agricultor."
                    )
                    st.rerun()



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

    return busqueda.strip().casefold()


def _vista_inicio(comprador_id):
    busqueda = _barra_busqueda(comprador_id)
    cosechas = listar_cosechas(solo_disponibles=True)

    if busqueda:
        cosechas = [
            cosecha
            for cosecha in cosechas
            if busqueda in cosecha["producto"].casefold()
            or busqueda in cosecha["finca"].casefold()
        ]

    if not cosechas:
        st.info(
            "No hay cosechas disponibles que coincidan en este momento."
        )
        return

    for finca_id, lotes in _agrupar_fincas(cosechas).items():
        _fila_finca(finca_id, lotes, comprador_id)


def _vista_fincas(comprador_id):
    cosechas = listar_cosechas(solo_disponibles=True)
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



def _vista_pedidos(comprador_id):
    st.subheader("📦 Mis pedidos")

    pedidos = listar_pedidos(comprador_id)

    if not pedidos:
        st.info("Aún no tienes pedidos. Elige un producto en Inicio.")
    else:
        for pedido in pedidos:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"### Pedido #{pedido['id']}")
                    st.write(f"**Producto:** {pedido['producto']}")
                    st.write(f"**Finca:** {pedido['finca']}")
                    st.write(
                        f"**Cantidad:** "
                        f"{pedido['cantidad']} {pedido['unidad']}"
                    )
                    st.write(f"**Total:** {cop(pedido['total'])}")

                with col2:
                    estado = pedido["estado"]

                    if estado == "aceptado":
                        st.success("Aceptado")
                    elif estado == "pendiente":
                        st.warning("Pendiente")
                    elif estado == "rechazado":
                        st.error("Rechazado")
                    else:
                        st.info(estado.capitalize())

                if pedido["estado"] == "aceptado":
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

    st.markdown("---")
    st.subheader("💰 Historial de pagos")

    pagos = listar_pagos(comprador_id)

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

    with st.sidebar:
        st.markdown("### 🛒 Comprador")
        st.caption(f"Hola, {usuario}")
        st.markdown("**Descubrir**")

        vista = st.radio(
            "Menú",
            ["🏠 Inicio", "🏡 Fincas", "📦 Mis pedidos"],
            label_visibility="collapsed",
            key=f"comp_vista_{comprador_id}",
        )

    st.title("🛒 Comprar Alimentos del Campo")

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

    if vista == "🏠 Inicio":
        _vista_inicio(comprador_id)
    elif vista == "🏡 Fincas":
        _vista_fincas(comprador_id)
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