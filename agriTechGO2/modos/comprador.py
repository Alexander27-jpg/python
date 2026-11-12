import streamlit as st

# ----------------------------------------------------------------------
# Utilidades comunes
# ----------------------------------------------------------------------
def cop(valor):
    """Formatea un número como pesos colombianos: $1.500.000 COP"""
    signo = "-" if valor < 0 else ""
    return f"{signo}${abs(valor):,.0f} COP".replace(",", ".")


def comun_estado_cosecha(cosecha):
    """Calcula el estado usando cantidad y disponibilidad."""
    if cosecha["cantidad"] <= 0:
        return "Agotada"
    return "Disponible" if cosecha.get("activa", True) else "Pausada"


def comun_listar_cosechas(agricultor_id=None, solo_disponibles=False):
    """Consulta las cosechas registradas en la sesión actual por los agricultores."""
    resultados = []
    datos_agricultores = st.session_state.get("agri_datos", {})

    for propietario, datos in datos_agricultores.items():
        if agricultor_id is not None and propietario != agricultor_id:
            continue

        for cosecha in datos.get("cosechas", []):
            registro = dict(cosecha)
            registro["agricultor_id"] = propietario
            registro["estado"] = comun_estado_cosecha(registro)

            if solo_disponibles and registro["estado"] != "Disponible":
                continue

            resultados.append(registro)

    return resultados


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
# Lógica de compra y pedidos
# ----------------------------------------------------------------------
def _registrar_compra(cosecha, cantidad):
    """Descuenta el inventario del agricultor y guarda el pedido. Devuelve True/False."""
    lotes = st.session_state["agri_datos"][cosecha["agricultor_id"]]["cosechas"]

    for orig in lotes:
        if orig["id"] == cosecha["id"]:
            if orig["cantidad"] < cantidad:
                return False
            orig["cantidad"] -= cantidad
            if orig["cantidad"] <= 1e-9:
                orig["cantidad"] = 0

            pedidos = st.session_state.setdefault("pedidos_comprador", [])
            pedidos.append({
                "Producto": cosecha.get("producto", "Producto"),
                "Finca": cosecha.get("finca", "N/D"),
                "Cantidad": f"{cantidad:g} {cosecha.get('unidad', 'kg')}",
                "Total": cop(cantidad * cosecha.get("precio", 0)),
                "Estado": "En tránsito",
            })
            return True
    return False


# ----------------------------------------------------------------------
# Componentes visuales
# ----------------------------------------------------------------------
def _tarjeta_producto(cosecha, clave):
    """Tarjeta de producto (imagen, nombre, precio y compra)."""
    unidad = cosecha.get("unidad", "kg")
    precio = cosecha.get("precio", 0)
    disponible = float(cosecha.get("cantidad", 0))

    with st.container(border=True):
        if cosecha.get("foto"):
            st.image(cosecha["foto"], use_container_width=True)
        else:
            st.markdown('<div class="sin-foto"><b>🌱 Cosecha Local</b></div>',
                        unsafe_allow_html=True)

        st.markdown(f"**{cosecha.get('producto', 'Producto')}**")
        st.caption(f"{cop(precio)} por {unidad} · {disponible:g} {unidad} disp.")
        st.caption(f"⭐ {cosecha.get('calidad', 'Estándar')}")

        with st.expander("🛒 Comprar"):
            minimo = min(1.0, disponible)
            cantidad = st.number_input(
                f"¿Cuántos {unidad}?",
                min_value=minimo,
                max_value=disponible,
                value=minimo,
                step=1.0 if disponible >= 1 else 0.5,
                key=f"cant_{clave}",
            )
            st.markdown(f"**Total:** {cop(cantidad * precio)}")

            if st.button("✅ Confirmar compra", key=f"btn_{clave}"):
                if _registrar_compra(cosecha, cantidad):
                    st.session_state["flash_comprador"] = (
                        f"¡Compra exitosa! Adquiriste {cantidad:g} {unidad} "
                        f"de {cosecha.get('producto')}."
                    )
                    st.rerun()
                else:
                    st.error("No hay suficiente cantidad disponible en este lote.")


def _banner_finca(nombre, lotes):
    """Encabezado azul de la finca (se ve bien en PC y en celular)."""
    productos = ", ".join(sorted({l.get("producto", "") for l in lotes}))
    ubicacion = lotes[0].get("ubicacion") or lotes[0].get("municipio") or "Norte de Santander"
    pista = '<p class="hint">Desliza para ver más productos ➜</p>' if len(lotes) > 1 else ""
    st.markdown(
        f"""
        <div class="finca-banner">
            <h3>🏡 {nombre}</h3>
            <p>📍 {ubicacion} · 📦 {len(lotes)} producto(s)</p>
            <p>🌾 {productos}</p>
            {pista}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _fila_finca(nombre, lotes):
    """Una finca = banner azul + carrusel horizontal con todos sus productos."""
    _banner_finca(nombre, lotes)

    # La key empieza con "carrusel_": el CSS la usa para activar el scroll horizontal
    clave_finca = "".join(ch if ch.isalnum() else "_" for ch in nombre)
    with st.container(key=f"carrusel_{clave_finca}"):
        cols = st.columns(len(lotes))
        for col, lote in zip(cols, lotes):
            with col:
                _tarjeta_producto(lote, f"{lote['id']}_{lote['agricultor_id']}")

    st.divider()


# ----------------------------------------------------------------------
# Vistas
# ----------------------------------------------------------------------
def _barra_busqueda():
    """Barra de búsqueda centrada, como en el mockup."""
    _, centro, _ = st.columns([1, 3, 1])
    with centro:
        c_input, c_btn = st.columns([5, 1])
        texto = c_input.text_input(
            "Buscar",
            placeholder="Producto o finca: Café, Yuca, Finca El Mirador...",
            label_visibility="collapsed",
            key="busqueda_comprador",
        )
        c_btn.button("Buscar", use_container_width=True)
    return texto.strip().lower()


def _vista_inicio():
    texto = _barra_busqueda()
    cosechas = comun_listar_cosechas(solo_disponibles=True)

    if texto:
        cosechas = [
            c for c in cosechas
            if texto in c.get("producto", "").lower() or texto in c.get("finca", "").lower()
        ]

    if not cosechas:
        st.info("No hay cosechas disponibles que coincidan en este momento.")
        return

    # Agrupar por finca: cada finca es una fila
    fincas = {}
    for c in cosechas:
        fincas.setdefault(c.get("finca", "N/D"), []).append(c)

    for nombre, lotes in fincas.items():
        _fila_finca(nombre, lotes)


def _vista_fincas():
    cosechas = comun_listar_cosechas(solo_disponibles=True)
    fincas = {}
    for c in cosechas:
        fincas.setdefault(c.get("finca", "N/D"), []).append(c)

    if not fincas:
        st.info("Aún no hay fincas con cosechas publicadas.")
        return

    elegida = st.selectbox("Selecciona una finca", list(fincas.keys()))
    _fila_finca(elegida, fincas[elegida])


def _vista_pedidos():
    st.subheader("📦 Mis pedidos")
    pedidos = st.session_state.get("pedidos_comprador", [])
    if not pedidos:
        st.info("Aún no has realizado compras. ¡Elige un lote en Inicio!")
    else:
        st.dataframe(pedidos, use_container_width=True, hide_index=True)


# ----------------------------------------------------------------------
# Punto de entrada (main.py llama a esta función)
# ----------------------------------------------------------------------
def ejecutar_modo_comprador():
    """Ejecuta el panel interactivo del Comprador Directo"""
    st.markdown(ESTILOS, unsafe_allow_html=True)

    usuario = st.session_state.get("usuario", "Comprador")

    # Menú lateral izquierdo (equivale al menú del mockup)
    with st.sidebar:
        st.markdown("### 🛒 Comprador")
        st.caption(f"Hola, {usuario}")
        st.markdown("**Descubrir**")
        vista = st.radio(
            "Menú",
            ["🏠 Inicio", "🏡 Fincas", "📦 Mis pedidos"],
            label_visibility="collapsed",
            key="vista_comprador",
        )

    st.title("🛒 Comprar Alimentos del Campo")

    # Mensaje de éxito que sobrevive al st.rerun()
    mensaje = st.session_state.pop("flash_comprador", None)
    if mensaje:
        st.success(mensaje)

    if vista == "🏠 Inicio":
        _vista_inicio()
    elif vista == "🏡 Fincas":
        _vista_fincas()
    else:
        _vista_pedidos()


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