import streamlit as st
import os
import time

def mostrar_splash():
    """Muestra la pantalla de carga inicial con animación"""
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


def mostrar_login(ruta_logo):
    """Muestra la interfaz de inicio de sesión"""
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
            
            h2, h3, p, label, .stMarkdown {
                color: #ffffff !important;
                font-weight: 500;
            }
            .stCaption {
                color: #a3cef1 !important;
            }

            div.stButton > button:first-child {
                background: linear-gradient(135deg, #2d6a4f 0%, #40916c 50%, #52b788 100%);
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
                background: linear-gradient(135deg, #40916c 0%, #52b788 100%);
                box-shadow: 0px 0px 30px rgba(82, 183, 136, 0.9);
                transform: scale(1.02);
            }
        </style>
    """, unsafe_allow_html=True)

    col_izq, col_der = st.columns([1, 1], gap="large")

    with col_izq:
        if os.path.exists(ruta_logo):
            st.markdown("""
                <div style="position: relative; left: 40px; top: 0px;">
            """, unsafe_allow_html=True)
            st.image(ruta_logo, width=90)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("## COLOQUEN EL LOGO")

        st.markdown("""
            <div class="left-card">
                <div>
                    <h1>¡Bienvenido a<br>agriTechGO! </h1>
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
        st.markdown("### **Inicia sesión para continuar**")
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("form_login_moderno", clear_on_submit=False):
            email = st.text_input("Correo o Usuario", placeholder="alexander", value=st.session_state.get("input_email", ""))
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            rol = st.selectbox(
                "Selecciona tu perfil en la plataforma:",
                [
                    " Agricultor / Caficultor", 
                    " Comprador Directo", 
                    " Inversionista Agro", 
                    " Administradores (Equipo)"
                ]
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Iniciar Sesión Ahora", use_container_width=True)

        if submit:
            usuario_ingresado = email.strip()
            if usuario_ingresado != "" and (password == "1234" or password == ""):
                st.session_state["usuario"] = usuario_ingresado
                st.session_state["rol"] = rol
                st.session_state["pantalla"] = "dashboard"
                st.rerun()
            elif usuario_ingresado == "":
                st.error("Por favor ingresa un correo o usuario.")
            else:
                st.error("Contraseña incorrecta. Usa `1234` o prueba dejarla libre.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("¿No tienes cuenta? Regístrate aquí", use_container_width=True):
            st.session_state.pantalla = "registro"
            st.rerun()


def mostrar_registro(ruta_logo):
    """Muestra la interfaz de registro de usuarios"""
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
            h2, h3, p, label, .stMarkdown {
                color: #ffffff !important;
                font-weight: 500;
            }
            .stCaption {
                color: #a3cef1 !important;
            }
            div.stButton > button:first-child {
                background: linear-gradient(135deg, #2d6a4f 0%, #40916c 50%, #52b788 100%);
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
                background: linear-gradient(135deg, #40916c 0%, #52b788 100%);
                box-shadow: 0px 0px 30px rgba(82, 183, 136, 0.9);
                transform: scale(1.02);
            }
        </style>
    """, unsafe_allow_html=True)

    col_izq, col_der = st.columns([1, 1], gap="large")

    with col_izq:
        if os.path.exists(ruta_logo):
            st.markdown("""
                <div style="position: relative; left: 40px; top: 0px;">
            """, unsafe_allow_html=True)
            st.image(ruta_logo, width=90)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("## COLOQUEN EL LOGO")

        st.markdown("""
            <div class="left-card">
                <div>
                    <h1>Únete a<br>agriTechGO! </h1>
                    <p style="margin-top: 20px;">
                        Crea tu cuenta hoy mismo y forma parte de la revolución digital del campo. 
                        Conéctate con compradores y productores de café sin intermediarios.
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
        st.markdown("### **Crea una nueva cuenta**")
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("form_registro_moderno", clear_on_submit=False):
            nombre_reg = st.text_input("Nombre completo", placeholder="Tu nombre y apellido")
            email_reg = st.text_input("Correo electrónico", placeholder="tucorreo@ejemplo.com")
            password_reg = st.text_input("Contraseña", type="password", placeholder="••••••••")
            confirm_reg = st.text_input("Confirmar contraseña", type="password", placeholder="••••••••")
            
            rol_reg = st.selectbox(
                "Selecciona tu perfil principal:",
                [
                    " Agricultor / Caficultor", 
                    " Comprador Directo", 
                    " Inversionista Agro"
                ]
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_reg = st.form_submit_button("Registrarse Ahora", use_container_width=True)

        if submit_reg:
            if not nombre_reg.strip() or not email_reg.strip() or not password_reg:
                st.error("Por favor completa todos los campos obligatorios.")
            elif password_reg != confirm_reg:
                st.error("Las contraseñas no coinciden.")
            else:
                st.success("¡Cuenta creada con éxito! Ahora puedes iniciar sesión.")
                st.session_state.pantalla = "login"
                st.rerun()

        col_volver1, col_volver2 = st.columns([2, 1])
        with col_volver1:
            st.markdown("<p style='color: #94a3b8; font-size: 0.85rem; margin-top: 15px;'>¿Ya tienes una cuenta?</p>", unsafe_allow_html=True)
        with col_volver2:
            if st.button("Ir al Login"):
                st.session_state.pantalla = "login"
                st.rerun()