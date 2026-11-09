import streamlit as st
import os
import time
import pandas as pd
from datetime import datetime

# Configuración de página ancha e icono
st.set_page_config(page_title="agriTechGO", page_icon="", layout="wide")

# Nombre del archivo de tu logo guardado en la misma carpeta
RUTA_LOGO = "logo.png"

if "pantalla" not in st.session_state:
    st.session_state.pantalla = "splash"


def cop(valor):
    """Formatea un número como pesos colombianos: $1.500.000 COP"""
    return f"${valor:,.0f} COP".replace(",", ".")
 
 
def inv_init_estado(usuario):
    """Crea los datos del inversionista la primera vez que entra.
    NOTA: cuando tengan base de datos, reemplazar por consultas."""
    ss = st.session_state
    ss.setdefault("inv_perfil", {"nombre": usuario, "descripcion": "", "foto": None})
    ss.setdefault("inv_wallet", {"saldo": 1_000_000, "movimientos": []})
    ss.setdefault("inv_siguiendo", set())   # ids de fincas seguidas
    ss.setdefault("inv_inversiones", [])    # inversiones realizadas
    # Fincas de ejemplo. Idealmente las publica el perfil Agricultor.
    ss.setdefault("inv_fincas", [
        {
            "id": 1, "nombre": "Finca Las Margaritas", "agricultor": "Don Aurelio",
            "ubicacion": "Vereda Las Margaritas", "proyecto": "Infraestructura de secado solar",
            "meta": 5_000_000, "recaudado": 3_750_000, "rentabilidad": 0.185,
            "riesgo": "Bajo", "avance": 0.60,
        },
        {
            "id": 2, "nombre": "Finca El Mirador", "agricultor": "Doña Marta",
            "ubicacion": "Vereda El Mirador", "proyecto": "Sistema de riego por goteo",
            "meta": 8_000_000, "recaudado": 2_400_000, "rentabilidad": 0.21,
            "riesgo": "Medio", "avance": 0.30,
        },
        {
            "id": 3, "nombre": "Finca Buenavista", "agricultor": "Don Jorge",
            "ubicacion": "Vereda Buenavista", "proyecto": "Beneficiadero ecológico de café",
            "meta": 6_000_000, "recaudado": 5_100_000, "rentabilidad": 0.17,
            "riesgo": "Bajo", "avance": 0.80,
        },
    ])
 
 
def inv_registrar_movimiento(tipo, monto, detalle):
    st.session_state.inv_wallet["movimientos"].insert(0, {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Tipo": tipo,
        "Monto": monto,
        "Detalle": detalle,
    })
 
 
def inv_buscar_finca(finca_id):
    return next(f for f in st.session_state.inv_fincas if f["id"] == finca_id)
 
 
def inv_valor_actual(inv):
    """Valor simulado: capital + ganancia proporcional al avance de la cosecha."""
    finca = inv_buscar_finca(inv["finca_id"])
    ganancia_final = inv["monto"] * inv["rentabilidad"]
    return inv["monto"] + ganancia_final * finca["avance"]
 
 
def inv_tab_perfil():
    perfil = st.session_state.inv_perfil
    st.subheader("👤 Mi perfil")
 
    col_foto, col_datos = st.columns([1, 2])
 
    with col_foto:
        if perfil["foto"]:
            st.image(perfil["foto"], use_container_width=True)
        else:
            st.info("Aún no tienes foto de perfil.")
        archivo = st.file_uploader("Subir foto", type=["png", "jpg", "jpeg"], key="inv_foto_uploader")
        if archivo is not None and st.button("📷 Guardar foto"):
            perfil["foto"] = archivo.getvalue()
            st.success("Foto actualizada.")
            st.rerun()
 
    with col_datos:
        nombre = st.text_input("Nombre a mostrar", value=perfil["nombre"])
        descripcion = st.text_area(
            "Descripción", value=perfil["descripcion"], height=150,
            placeholder="Cuéntales a los agricultores quién eres y por qué te interesa invertir en el campo...",
        )
        if st.button("💾 Guardar perfil"):
            perfil["nombre"] = nombre.strip() or perfil["nombre"]
            perfil["descripcion"] = descripcion
            st.success("Perfil guardado.")
 
    st.markdown("---")
    st.markdown(f"### {perfil['nombre']}")
    st.write(perfil["descripcion"] or "_Sin descripción todavía._")
 
 
def inv_tab_fincas():
    ss = st.session_state
    st.subheader("🌱 Fincas y proyectos")
 
    filtro = st.radio("Mostrar", ["Todas", "Solo las que sigo"], horizontal=True)
 
    fincas = ss.inv_fincas
    if filtro == "Solo las que sigo":
        fincas = [f for f in fincas if f["id"] in ss.inv_siguiendo]
        if not fincas:
            st.info("Todavía no sigues ninguna finca.")
 
    for f in fincas:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"#### {f['nombre']}")
            c1.caption(f"👨‍🌾 {f['agricultor']} · 📍 {f['ubicacion']}")
            c1.write(f"**Proyecto:** {f['proyecto']}")
 
            siguiendo = f["id"] in ss.inv_siguiendo
            if c2.button("⭐ Dejar de seguir" if siguiendo else "☆ Seguir", key=f"seguir_{f['id']}"):
                if siguiendo:
                    ss.inv_siguiendo.discard(f["id"])
                else:
                    ss.inv_siguiendo.add(f["id"])
                st.rerun()
 
            m1, m2, m3 = st.columns(3)
            m1.metric("Rentabilidad", f"{f['rentabilidad']*100:.1f}% E.A.")
            m2.metric("Riesgo", f["riesgo"])
            m3.metric("Avance de cosecha", f"{f['avance']*100:.0f}%")
 
            progreso = min(f["recaudado"] / f["meta"], 1.0)
            st.progress(progreso, text=f"{cop(f['recaudado'])} de {cop(f['meta'])} ({progreso*100:.0f}%)")
 
            faltante = f["meta"] - f["recaudado"]
            if faltante <= 0:
                st.success("✅ Meta alcanzada")
                continue
 
            ci1, ci2 = st.columns([2, 1])
            monto = ci1.number_input(
                "Monto a invertir (COP)", min_value=0, max_value=int(faltante),
                step=50_000, key=f"monto_{f['id']}",
            )
            ci2.write("")
            ci2.write("")
            if ci2.button("💰 Invertir", key=f"invertir_{f['id']}"):
                if monto <= 0:
                    st.error("Ingresa un monto mayor a 0.")
                elif monto > ss.inv_wallet["saldo"]:
                    st.error("Saldo insuficiente en tu wallet. Recarga para continuar.")
                else:
                    ss.inv_wallet["saldo"] -= monto
                    f["recaudado"] += monto
                    ss.inv_inversiones.append({
                        "finca_id": f["id"],
                        "monto": monto,
                        "rentabilidad": f["rentabilidad"],
                        "fecha": datetime.now().strftime("%Y-%m-%d"),
                    })
                    inv_registrar_movimiento("Inversión", -monto, f"{f['nombre']} - {f['proyecto']}")
                    ss.inv_siguiendo.add(f["id"])  # al invertir, la sigue automáticamente
                    st.success(f"¡Gracias por impulsar el campo! Invertiste {cop(monto)} en {f['nombre']}.")
                    st.rerun()
 
 
def inv_tab_inversiones():
    ss = st.session_state
    st.subheader("📊 Mis inversiones")
 
    if not ss.inv_inversiones:
        st.info("Aún no has invertido. Ve a la pestaña **Fincas** para empezar.")
        return
 
    filas = []
    for inv in ss.inv_inversiones:
        finca = inv_buscar_finca(inv["finca_id"])
        actual = inv_valor_actual(inv)
        filas.append({
            "Finca": finca["nombre"],
            "Proyecto": finca["proyecto"],
            "Fecha": inv["fecha"],
            "Invertido": inv["monto"],
            "Valor actual": round(actual),
            "Ganancia": round(actual - inv["monto"]),
            "Rentab. E.A.": f"{inv['rentabilidad']*100:.1f}%",
            "Avance cosecha": f"{finca['avance']*100:.0f}%",
        })
    df = pd.DataFrame(filas)
 
    total_inv = df["Invertido"].sum()
    total_act = df["Valor actual"].sum()
    ganancia = total_act - total_inv
 
    c1, c2, c3 = st.columns(3)
    c1.metric("Total invertido", cop(total_inv))
    c2.metric("Valor actual", cop(total_act))
    c3.metric("Ganancia acumulada", cop(ganancia), delta=f"{(ganancia/total_inv)*100:.1f}%")
 
    st.markdown("#### Detalle")
    st.dataframe(df, use_container_width=True, hide_index=True)
 
    st.markdown("#### Invertido por finca")
    st.bar_chart(df.groupby("Finca")["Invertido"].sum())
 
 
def inv_tab_wallet():
    wallet = st.session_state.inv_wallet
    st.subheader("👛 Mi wallet digital")
    st.metric("Saldo disponible", cop(wallet["saldo"]))
 
    col_dep, col_ret = st.columns(2)
 
    with col_dep:
        with st.container(border=True):
            st.markdown("**➕ Recargar saldo**")
            dep = st.number_input("Monto a recargar", min_value=0, step=50_000, key="wallet_dep")
            if st.button("Recargar"):
                if dep > 0:
                    wallet["saldo"] += dep
                    inv_registrar_movimiento("Recarga", dep, "Recarga simulada")
                    st.success(f"Recargaste {cop(dep)}.")
                    st.rerun()
                else:
                    st.error("Ingresa un monto válido.")
 
    with col_ret:
        with st.container(border=True):
            st.markdown("**➖ Retirar saldo**")
            ret = st.number_input("Monto a retirar", min_value=0, step=50_000, key="wallet_ret")
            if st.button("Retirar"):
                if ret <= 0:
                    st.error("Ingresa un monto válido.")
                elif ret > wallet["saldo"]:
                    st.error("No tienes saldo suficiente.")
                else:
                    wallet["saldo"] -= ret
                    inv_registrar_movimiento("Retiro", -ret, "Retiro simulado")
                    st.success(f"Retiraste {cop(ret)}.")
                    st.rerun()
 
    st.markdown("#### Historial de movimientos")
    if wallet["movimientos"]:
        df = pd.DataFrame(wallet["movimientos"])
        df["Monto"] = df["Monto"].apply(cop)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("Sin movimientos todavía.")    


# -------------------------------------------------------------------------
# PANTALLA DE CARGA (SPLASH SCREEN) CON PLANTA VECTORIAL ANIMADA
# -------------------------------------------------------------------------
if st.session_state.pantalla == "splash":
    st.markdown("""
        <style>
            @keyframes fadeInOut {
                0% { opacity: 0; transform: scale(0.9); }
                50% { opacity: 1; transform: scale(1); }
                100% { opacity: 0.9; transform: scale(1); }
            }
            @keyframes growPlant {
                0% { transform: scale(0) translateY(30px); opacity: 0; }
                60% { transform: scale(1.05) translateY(-5px); opacity: 1; }
                100% { transform: scale(1) translateY(0); opacity: 1; }
            }
            @keyframes pulseGlow {
                0% { filter: drop-shadow(0 0 10px rgba(82, 183, 136, 0.4)); }
                50% { filter: drop-shadow(0 0 30px rgba(82, 183, 136, 0.9)); }
                100% { filter: drop-shadow(0 0 10px rgba(82, 183, 136, 0.4)); }
            }

            .stApp {
                background: linear-gradient(-45deg, #022b12, #081c15, #1b4332, #2d6a4f, #0b0f0d);
                background-size: 500% 500%;
            }

            .splash-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 75vh;
                text-align: center;
                animation: fadeInOut 1.5s ease-in-out;
            }
            
            .plant-wrapper {
                animation: growPlant 2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards, pulseGlow 3s infinite ease-in-out;
                margin-bottom: 25px;
            }

            .splash-title {
                font-size: 3rem;
                font-weight: 900;
                background: linear-gradient(135deg, #52b788, #b7e4c7);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: 2px;
            }
            
            .splash-subtitle {
                font-size: 1.1rem;
                color: #94a3b8;
                margin-top: 10px;
                font-weight: 500;
            }
        </style>

        <div class="splash-container">
            <div class="plant-wrapper">
                <svg width="110" height="110" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M25 80C25 80 40 73 50 73C60 73 75 80 75 80" stroke="#52b788" stroke-width="4" stroke-linecap="round"/>
                    <path d="M50 73V38" stroke="#74c69d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M50 55C40 55 28 45 32 32C36 19 50 38 50 55Z" fill="#52b788" stroke="#b7e4c7" stroke-width="2"/>
                    <path d="M50 45C60 42 74 32 70 19C66 6 50 28 50 45Z" fill="#74c69d" stroke="#e2fceb" stroke-width="2"/>
                    <path d="M50 38C45 28 50 15 50 10C50 15 55 28 50 38Z" fill="#b7e4c7"/>
                </svg>
            </div>
            <div class="splash-title">agriTechGO</div>
            <div class="splash-subtitle">Cultivando el futuro del agro sin intermediarios...</div>
        </div>
    """, unsafe_allow_html=True)

    time.sleep(3.5)
    st.session_state.pantalla = "login"
    st.rerun()

# -------------------------------------------------------------------------
# PANTALLA DE LOGIN
# -------------------------------------------------------------------------
elif st.session_state.pantalla == "login":
    
    st.markdown("""
        <style>
            @keyframes neonPulse {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            @keyframes borderGlow {
                0% { border-color: rgba(82, 183, 136, 0.3); box-shadow: 0 0 15px rgba(82, 183, 136, 0.2); }
                50% { border-color: rgba(82, 183, 136, 0.8); box-shadow: 0 0 35px rgba(82, 183, 136, 0.6); }
                100% { border-color: rgba(82, 183, 136, 0.3); box-shadow: 0 0 15px rgba(82, 183, 136, 0.2); }
            }

            .stApp {
                background: linear-gradient(-45deg, #022b12, #081c15, #1b4332, #2d6a4f, #0b0f0d);
                background-size: 500% 500%;
                animation: neonPulse 8s ease infinite;
                color: #ffffff;
            }
            
            .left-card {
                background: rgba(11, 31, 21, 0.85);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                padding: 3rem 2rem;
                border-radius: 22px;
                color: white;
                animation: borderGlow 4s infinite;
                border: 2px solid rgba(82, 183, 136, 0.5);
            }
            .left-card h1 {
                font-size: 2.6rem;
                font-weight: 900;
                color: #ffffff !important;
                text-shadow: 0 0 15px rgba(82, 183, 136, 0.6);
            }
            .left-card p {
                font-size: 1.05rem;
                color: #e2fceb;
                line-height: 1.6;
            }
            .left-footer {
                font-size: 0.8rem;
                color: #b7e4c7;
                margin-top: 25px;
                border-top: 1px solid rgba(255,255,255,0.2);
                padding-top: 10px;
            }

            div[data-testid="column"]:nth-of-type(2) {
                background: rgba(13, 27, 20, 0.9);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                padding: 2.5rem;
                border-radius: 22px;
                box-shadow: 0px 20px 40px rgba(0, 0, 0, 0.8);
                border: 2px solid rgba(82, 183, 136, 0.4);
            }
            
            h2, h3, p, label, .stMarkdown {
                color: #ffffff !important;
                font-weight: 500;
            }
            .stCaption {
                color: #a3cef1 !important;
            }

            div.stButton > button:first-child {
                background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 50%, #52b788 100%);
                color: white;
                border-radius: 12px;
                height: 52px;
                font-weight: bold;
                font-size: 1.1rem;
                border: 1px solid #74c69d;
                box-shadow: 0px 0px 20px rgba(82, 183, 136, 0.6);
                transition: 0.3s;
            }
            div.stButton > button:first-child:hover {
                background: linear-gradient(135deg, #2d6a4f 0%, #52b788 100%);
                box-shadow: 0px 0px 30px rgba(82, 183, 136, 0.9);
                transform: scale(1.02);
            }
        </style>
    """, unsafe_allow_html=True)

    col_izq, col_der = st.columns([1, 1], gap="large")

    with col_izq:
        if os.path.exists(RUTA_LOGO):
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            st.image(RUTA_LOGO, width=90)
        else:
            st.markdown("## COLOQUEN EL LOGO")

        st.markdown("""
            <div class="left-card">
                <div>
                    <h1>¡Hola,<br>agriTechGO!👋</h1>
                    <p style="margin-top: 20px;">
                        El impulso que el campo necesita, directo del cultivo a la mesa. 
                        Conectando a nuestros agricultores de café directamente con el mercado, 
                        eliminando intermediarios y generando comercio justo.
                    </p>
                </div>
                <div class="left-footer">
                    © 2026 agriTechGO. 
                    <br><b>Créditos:</b> Ing. Alexander, Ing. Kevin, Ing. Luis, Ing. Jonathan.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_der:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## **agriTechGO**", unsafe_allow_html=True)
        st.markdown("### **¡Bienvenido de nuevo!**")
        st.info("💡 **Credenciales de prueba para la presentación:**\n* **Usuario:** `demo@agritech.com` | **Clave:** `1234`")
        
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("form_login_moderno", clear_on_submit=False):
            email = st.text_input("Correo o Usuario", placeholder="demo@agritech.com")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            rol = st.selectbox(
                "Selecciona tu perfil en la plataforma:",
                [
                    "👨‍🌾 Agricultor / Caficultor", 
                    "🛒 Comprador Directo", 
                    "📈 Inversionista Agro", 
                    "🛠️ Administradores (Equipo)"
                ]
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Iniciar Sesión Ahora", use_container_width=True)

        if submit:
            # Validación rápida de prueba
            if email.strip() != "" and password == "1234":
                st.session_state.pantalla = "dashboard"
                st.session_state.usuario = email
                st.session_state.rol = rol
                st.rerun()
            elif email.strip() == "":
                st.error("Por favor ingresa un correo o usuario.")
            else:
                st.error("Contraseña incorrecta (Usa: `1234`).")

        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 15px;'>¿Olvidaste tu contraseña? <b>Haz clic aquí</b></p>", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# PANTALLA 2: DASHBOARDS SEGÚN EL ROL SELECCIONADO
# -------------------------------------------------------------------------
elif st.session_state.pantalla == "dashboard":
    
    rol_actual = st.session_state.get("rol", "")
    
    # --- 1. VISTA DE AGRICULTOR / CAFICULTOR ---
    if "Agricultor" in rol_actual:
        from datetime import date
        from html import escape
        from uuid import uuid4

        # FUNCIONES DEL MÓDULO
        def agri_pesos(valor):
            """Convierte un número al formato de pesos colombianos."""
            return "$" + f"{valor:,.0f}".replace(",", ".") + " COP"

        def agri_estado(cosecha):
            """Una cosecha sin existencias siempre aparece agotada."""
            if cosecha["cantidad"] <= 0:
                return "Agotada"
            return "Disponible" if cosecha["activa"] else "Pausada"

        def agri_validar(finca, producto, cantidad, precio):
            """Revisa los campos necesarios antes de registrar."""
            errores = []
            if not finca.strip():
                errores.append("Escribe el nombre de la finca o lote.")
            if not producto.strip():
                errores.append("Escribe el nombre del producto.")
            if cantidad <= 0:
                errores.append("La cantidad debe ser mayor que cero.")
            if precio <= 0:
                errores.append("El precio debe ser mayor que cero.")
            return errores

        # DATOS TEMPORALES SEPARADOS POR USUARIO
        agri_usuario = str(st.session_state.get("usuario", ""))

        if "agri_datos" not in st.session_state:
            st.session_state["agri_datos"] = {}

        if agri_usuario not in st.session_state["agri_datos"]:
            st.session_state["agri_datos"][agri_usuario] = {
                "cosechas": [],
                "aviso": ""
            }

        agri_datos = st.session_state["agri_datos"][agri_usuario]
        agri_cosechas = agri_datos["cosechas"]

        # ENCABEZADO: estilos exclusivos de esta tarjeta
        st.markdown(
            f"""
            <div style="
                background:#174B35;
                padding:28px;
                border-radius:18px;
                margin-bottom:20px;
            ">
                <div style="color:#D5E8B8;font-size:15px;">
                    AGRITECHGO · AGRICULTOR / CAFICULTOR
                </div>
                <div style="
                    color:#FFFFFF;
                    font-size:34px;
                    font-weight:750;
                    margin:8px 0;
                ">
                    Mi campo 🌱
                </div>
                <div style="color:#FFFFFF;font-size:17px;">
                    Bienvenido, {escape(agri_usuario)}.
                    Gestiona tus cosechas desde un solo lugar.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "Prototipo: los registros son temporales y no se comparten "
            "todavía con compradores. Al recargar la página o perder "
            "la sesión, pueden desaparecer."
        )

        if agri_datos["aviso"]:
            st.success(agri_datos["aviso"])
            agri_datos["aviso"] = ""

        # RESUMEN CALCULADO CON LOS REGISTROS DE ESTA SESIÓN
        agri_disponibles = sum(
            agri_estado(c) == "Disponible" for c in agri_cosechas
        )
        agri_fincas = {
            c["finca"].strip().casefold() for c in agri_cosechas
        }

        agri_col1, agri_col2, agri_col3 = st.columns(3)
        agri_col1.metric("Cosechas registradas", len(agri_cosechas))
        agri_col2.metric("Cosechas disponibles", agri_disponibles)
        agri_col3.metric("Fincas / lotes", len(agri_fincas))

        st.markdown("---")

        agri_tab1, agri_tab2, agri_tab3, agri_tab4 = st.tabs([
            "🌿 Mis cosechas",
            "➕ Registrar cosecha",
            "📦 Pedidos",
            "💰 Pagos"
        ])

        # SECCIÓN 1: TARJETAS MIXTAS DE COSECHAS
        with agri_tab1:
            st.subheader("🌿 Mis cosechas")
            st.write(
                "Consulta tus productos, fotografías, precios "
                "y disponibilidad."
            )

            if not agri_cosechas:
                st.info(
                    "Aún no tienes cosechas registradas. "
                    "Ingresa a Registrar cosecha para comenzar."
                )
            else:
                agri_filtro = st.selectbox(
                    "Filtrar cosechas",
                    ["Todas", "Disponible", "Pausada", "Agotada"],
                    key=f"agri_filtro_{agri_usuario}"
                )

                agri_visibles = [
                    c for c in agri_cosechas
                    if agri_filtro == "Todas"
                    or agri_estado(c) == agri_filtro
                ]

                if not agri_visibles:
                    st.info("No hay cosechas con ese estado.")

                for agri_c in agri_visibles:
                    agri_id = agri_c["id"]
                    agri_estado_actual = agri_estado(agri_c)

                    # TARJETA PRINCIPAL
                    with st.container(border=True):
                        agri_foto_col, agri_info_col = st.columns(
                            [1, 2],
                            gap="large"
                        )

                        # COLUMNA DE FOTOGRAFÍA
                        with agri_foto_col:
                            if agri_c.get("foto"):
                                st.image(
                                    agri_c["foto"],
                                    width=240
                                )
                            else:
                                st.markdown(
                                    """
                                    <div style="
                                        background:#EAF3E8;
                                        border-radius:12px;
                                        min-height:180px;
                                        display:flex;
                                        align-items:center;
                                        justify-content:center;
                                        flex-direction:column;
                                        color:#24543B;
                                        text-align:center;
                                        padding:15px;
                                    ">
                                        <div style="font-size:55px;">🌱</div>
                                        <b>Fotografía pendiente</b>
                                        <small>Agrega una imagen de tu producto</small>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                        # COLUMNA DE INFORMACIÓN
                        with agri_info_col:
                            st.markdown(
                                f"### {agri_c['producto']}"
                            )
                            st.caption(
                                f"🏡 {agri_c['finca']}"
                            )

                            if agri_estado_actual == "Disponible":
                                st.success("● Disponible")
                            elif agri_estado_actual == "Pausada":
                                st.warning("● Publicación pausada")
                            else:
                                st.error("● Agotada")

                            st.markdown(
                                f"**{agri_pesos(agri_c['precio'])}**"
                            )
                            st.caption(
                                f"Precio por {agri_c['unidad']}"
                            )

                            met1, met2 = st.columns(2)

                            met1.metric(
                                "Cantidad disponible",
                                f"{agri_c['cantidad']:g} "
                                f"{agri_c['unidad']}"
                            )

                            met2.metric(
                                "Calidad",
                                agri_c["calidad"]
                            )

                            st.caption(
                                "📅 Cosecha: "
                                + agri_c["fecha"].strftime("%d/%m/%Y")
                            )

                        # EDICIÓN DE LA COSECHA
                        with st.expander("✏️ Editar información"):
                            with st.form(
                                f"agri_editar_{agri_id}"
                            ):
                                agri_nueva_cantidad = st.number_input(
                                    "Cantidad disponible",
                                    min_value=0.0,
                                    value=float(agri_c["cantidad"]),
                                    step=1.0
                                )

                                agri_nuevo_precio = st.number_input(
                                    "Precio por unidad (COP)",
                                    min_value=1,
                                    value=int(agri_c["precio"]),
                                    step=100
                                )

                                agri_activa = st.checkbox(
                                    "Mantener disponible",
                                    value=agri_c["activa"]
                                )

                                agri_guardar = st.form_submit_button(
                                    "Guardar cambios",
                                    use_container_width=True
                                )

                            if agri_guardar:
                                agri_c["cantidad"] = agri_nueva_cantidad
                                agri_c["precio"] = agri_nuevo_precio
                                agri_c["activa"] = agri_activa

                                agri_datos["aviso"] = (
                                    "Información de la cosecha actualizada."
                                )
                                st.rerun()

        # SECCIÓN 2: REGISTRO
        with agri_tab2:
            st.subheader("Registra tu cosecha")
            st.write(
                "Indica qué vendes, cuánto tienes disponible "
                "y el precio de cada unidad."
            )

            with st.form(f"agri_registro_{agri_usuario}"):
                agri_finca = st.text_input(
                    "Nombre del lote / finca",
                    placeholder="Ejemplo: Finca La Esperanza",
                    max_chars=100
                )
                agri_producto = st.text_input(
                    "Producto",
                    placeholder="Ejemplo: Café pergamino, tomate o plátano",
                    max_chars=80
                )
                agri_calidad = st.selectbox(
                    "Calidad del grano — para café",
                    [
                        "No aplica",
                        "Café Especial (Exóticas)",
                        "Café Estándar Premium",
                        "Café Comercial"
                    ]
                )
                agri_unidad = st.selectbox(
                    "Unidad de venta",
                    ["kg", "arroba", "unidad"]
                )
                agri_cantidad = st.number_input(
                    "Cantidad disponible en la unidad seleccionada",
                    min_value=0.0,
                    value=0.0,
                    step=1.0
                )
                agri_precio = st.number_input(
                    "Precio por unidad seleccionada (COP)",
                    min_value=0,
                    value=0,
                    step=100
                
                )

                agri_fecha = st.date_input(
                 "Fecha de cosecha",
                 value=date.today()

                )

                agri_foto = st.file_uploader(
                    "Fotografía del producto",
                    type=["png", "jpg", "jpeg", "webp"],
                    help="Sube una fotografía de tu cosecha."
                )

                if agri_foto is not None:
                    st.image(
                        agri_foto,
                        caption="Vista previa de tu producto",
                        width=300
                    )

                st.caption(
                    "El precio corresponde a una unidad de venta. "
                    "No incluye cálculos de comisión ni transporte."
                )

                agri_registrar = st.form_submit_button(
                    "🌱 Registrar cosecha",
                    use_container_width=True
                )

            if agri_registrar:
                agri_errores = agri_validar(
                    agri_finca,
                    agri_producto,
                    agri_cantidad,
                    agri_precio
                )

                if agri_errores:
                    for agri_error in agri_errores:
                        st.error(agri_error)
                else:
                    agri_cosechas.append({
                        "id": uuid4().hex,
                        "finca": agri_finca.strip(),
                        "producto": agri_producto.strip(),
                        "calidad": agri_calidad,
                        "unidad": agri_unidad,
                        "cantidad": agri_cantidad,
                        "precio": agri_precio,
                        "fecha": agri_fecha,
                        "foto": (
                            agri_foto.getvalue()
                            if agri_foto is not None
                            else None
                        ),
                        "activa": True
                    })
                    agri_datos["aviso"] = (
                        "Cosecha registrada en esta sesión. "
                        "Puedes consultarla en «Mis cosechas»."
                    )
                    st.rerun()

        # SECCIÓN 3: PEDIDOS PENDIENTES DE INTEGRACIÓN
        with agri_tab3:
            st.subheader("Mis pedidos")
            st.info("La recepción de pedidos todavía no está conectada.")
            st.write(
                "Aquí aparecerán el comprador, el producto solicitado, "
                "la cantidad y el estado de cada pedido."
            )

        # SECCIÓN 4: PAGOS PENDIENTES DE INTEGRACIÓN
        with agri_tab4:
            st.subheader("Mis pagos")
            st.info("Los pagos todavía no están conectados.")
            st.write(
                "Aquí podrás consultar los valores pendientes "
                "y recibidos cuando se integre esta función."
            )

    # --- 2. VISTA DE COMPRADOR DIRECTO ---
    elif "Comprador" in rol_actual:
        st.title("🛒 Mercado de Café Directo - agriTechGO")
        st.success(f"Conectado como Comprador: **{st.session_state.usuario}**")
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("Caficultores Disponibles", "18 Aliados")
        col2.metric("Kilos Adquiridos", "1,200 kg")
        col3.metric("Ahorro Intermediarios", "14%")

        st.markdown("### 🌾 Lotes Disponibles de la Región (Cúcuta y Norte de Santander)")
        
        # Simulando una tablita o tarjetas de café
        st.markdown("""
        | Finca / Productor | Variedad | Calidad | Precio / Arroba | Estado | Acción |
        | :--- | :--- | :--- | :--- | :--- | :--- |
        | **Finca El Mirador** | Castillo | Especial | \$190,000 COP | Disponible | 🛒 Comprar |
        | **Café San Isidro** | Caturra | Premium | \$175,000 COP | Disponible | 🛒 Comprar |
        | **Asociación Motilones** | Borbón | Exótico | \$220,000 COP | Disponible | 🛒 Comprar |
        """)
        
        if st.button("📦 Ver mis pedidos en tránsito"):
            st.info("No tienes pedidos en camino actualmente. ¡Selecciona un lote arriba para iniciar!")

    # --- 3. VISTA DE INVERSIONISTA AGRO ---
    elif "Inversionista" in rol_actual:
        st.title("📈 Panel de Inversión Agrícola - agriTechGO")
        st.success(f"Perfil Inversionista: **{st.session_state.usuario}**")
        
        if "inv_perfil" not in st.session_state:
            inv_init_estado(st.session_state.get("usuario", "Usuario_Demo"))

        tab_perfil, tab_fincas, tab_inv, tab_wallet = st.tabs(
            ["👤 Perfil", "🌱 Fincas", "📊 Mis inversiones", "👛 Wallet"]
        )
        with tab_perfil:
            inv_tab_perfil()
        with tab_fincas:
            inv_tab_fincas()
        with tab_inv:
            inv_tab_inversiones()
        with tab_wallet:
            inv_tab_wallet()
        # -------------------------------------

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("Proyectos Financiados", "2 Activos")
        col2.metric("Rentabilidad Promedio", "18.5% E.A.")
        col3.metric("Capital en Riesgo Controlado", "Bajo")

        st.markdown("### 💡 Oportunidades de Crowdfunding Agrícola")
        st.write("Financia infraestructura y tecnología para pequeños productores de café asegurando retorno directo sobre cosecha.")
        
        st.warning("⚡ **Proyecto Destacado:** Infraestructura de secado solar - Vereda Las Margaritas (Meta: $5,000,000 COP - 75% Recaudado)")
        if st.button("💰 Invertir en este Proyecto"):
            st.success("¡Gracias por impulsar el campo! Transacción simulada con éxito.")
            







    # --- 4. VISTA DE ADMINISTRADORES (EQUIPO) ---
    elif "Administradores" in rol_actual:
        st.title(" Panel de Control y Administración - agriTechGO")
        st.success(f"Sesión de Administrador activa: **{st.session_state.usuario}** - Alexander")
        
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Usuarios Totales", "142")
        col2.metric("Transacciones", "38")
        col3.metric("Estado del Sistema", "Óptimo ")
        col4.metric("Versión App", "v1.0.0 Pro")

        st.markdown("###  Equipo de Desarrollo (Ingeniería de Sistemas)")
        st.info("Control maestro del sistema, consultas de base de datos simuladas y parámetros generales de la plataforma.")
        
        tab1, tab2 = st.tabs(["📊 Estadísticas Globales", "⚙️ Configuración del Sistema"])
        with tab1:
            st.write("• **Caficultores registrados:** 85")
            st.write("• **Compradores activos:** 42")
            st.write("• **Inversionistas:** 15")
        with tab2:
            if st.button("🔄 Reiniciar Caché de Conexión DB"):
                st.success("Caché limpiada correctamente.")
            if st.button("📥 Exportar Reporte General (CSV)"):
                st.success("Reporte generado con éxito.")

    st.markdown("---")
    if st.button("⬅ Cerrar sesión y volver al Inicio"):
        st.session_state.pantalla = "splash"

        st.rerun()










print(".")