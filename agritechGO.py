import streamlit as st
import os
import time

# Configuración de página ancha e icono
st.set_page_config(page_title="agriTechGO", page_icon="", layout="wide")

# Nombre del archivo de tu logo guardado en la misma carpeta
RUTA_LOGO = "logo.png"

if "pantalla" not in st.session_state:
    st.session_state.pantalla = "splash"

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
        st.title("👨‍🌾 Panel del Caficultor - agriTechGO")
        st.success(f"Bienvenido, agricultor: **{st.session_state.usuario}**")
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("Mis Lotes Registrados", "3 Fincas")
        col2.metric("Cosecha Activa (Carga)", "45 Arrobas")
        col3.metric("Ofertas de Compradores", "5 Pendientes")
        
        st.markdown("### ☕ Gestión de Cosechas y Lotes")
        st.info("Aquí puedes publicar tus lotes de café pergamino o suave directamente al mercado sin intermediarios.")
        
        col_A, col_B = st.columns(2)
        with col_A:
            st.text_input("Nombre del Lote / Finca", "La Esperanza - Vereda Atalaya")
            st.number_input("Cantidad disponible (Arrobas)", 1, 500, 45)
        with col_B:
            st.selectbox("Calidad del Grano", ["Café Especial (Exóticas)", "Café Estándar Premium", "Café Comercial"])
            st.number_input("Precio por Arroba (COP)", 100000, 300000, 185000)
            
        if st.button("🚀 Publicar Cosecha al Mercado"):
            st.success("¡Tu lote ha sido publicado con éxito para los compradores directos!")

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
        col3.metric("Estado del Sistema", "Óptimo 🟢")
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
print("hola alexander")


print("Luis Balaguera")
