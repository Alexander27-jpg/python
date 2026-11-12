import base64
import os
import time
import streamlit as st


def mostrar_splash():
    """Muestra la pantalla de carga inicial"""
    ruta_video = "intro.mp4"
    video_base64 = ""
    if os.path.exists(ruta_video):
        with open(ruta_video, "rb") as f:
            video_base64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
            .stApp {{ background-color: #000000; }}
            .splash-container {{
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: #000; display: flex; flex-direction: column;
                align-items: center; justify-content: center; z-index: 99999;
            }}
            .splash-video {{
                position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                width: 100%; height: 100%; object-fit: contain; opacity: 0.8;
            }}
            .video-overlay {{
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(2, 43, 18, 0.55); z-index: 1;
            }}
            .splash-content {{
                position: relative; z-index: 2; text-align: center;
            }}
            .splash-title {{
                font-size: 3.5rem; font-weight: 900; color: #ffffff;
                text-shadow: 0 0 25px rgba(82, 183, 136, 0.9);
            }}
            .splash-subtitle {{
                font-size: 1.2rem; color: #b7e4c7; margin-top: 10px; font-weight: 500;
            }}
        </style>
        <div class="splash-container">
            <video autoplay muted playsinline class="splash-video">
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            </video>
            <div class="video-overlay"></div>
            <div class="splash-content">
                <div class="splash-title">AgriTechGO</div>
                <div class="splash-subtitle">Cultivando el futuro del agro sin intermediarios...</div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
    time.sleep(4.0)
    st.session_state.pantalla = "login"
    st.rerun()


def aplicar_estilos_burbuja():
    """Estilos para la imagen de fondo y la tarjeta blanca centrada"""
    archivo_fondo = "ruta_logo.jpeg"
    bg_base64 = ""
    if os.path.exists(archivo_fondo):
        with open(archivo_fondo, "rb") as f:
            bg_base64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
            /* Fondo con tu imagen real y un sombreado oscuro elegante */
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_base64}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}

            /* Tarjeta blanca sólida centrada */
            [data-testid="stForm"] {{
                background-color: #ffffff !important;
                padding: 2rem 2.5rem !important;
                border-radius: 24px !important;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5) !important;
                border: none !important;
            }}

            /* Textos oscuros dentro de la tarjeta blanca para campos */
            [data-testid="stForm"] label p {{
                color: #1b4332 !important;
                font-weight: 700 !important;
                font-size: 0.95rem !important;
            }}

            /* Títulos y subtítulos dentro de la tarjeta blanca (colores oscuros institucionales) */
            .titulo-burbuja {{
                font-size: 1.8rem;
                font-weight: 800;
                color: #1b4332 !important;
                text-align: center;
                margin-bottom: 0px;
                margin-top: 5px;
            }}
            .subtitulo-burbuja {{
                font-size: 0.9rem;
                color: #4a5568 !important;
                text-align: center;
                margin-bottom: 15px;
            }}

            /* Botón verde principal dentro de la tarjeta */
            [data-testid="stFormSubmitButton"] > button {{
                background-color: #52b788 !important;
                color: white !important;
                border-radius: 12px !important;
                height: 45px !important;
                font-weight: bold !important;
                font-size: 1rem !important;
                border: none !important;
                box-shadow: 0 4px 12px rgba(82, 183, 136, 0.4);
            }}
            [data-testid="stFormSubmitButton"] > button:hover {{
                background-color: #40916c !important;
            }}

            /* Botón secundario fuera del form principal */
            div.stButton > button {{
                background-color: rgba(255, 255, 255, 0.2) !important;
                color: white !important;
                border-radius: 12px !important;
                height: 42px !important;
                font-weight: 600 !important;
                border: 1px solid rgba(255, 255, 255, 0.4) !important;
            }}
            div.stButton > button:hover {{
                background-color: rgba(255, 255, 255, 0.35) !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def mostrar_login(ruta_logo):
    """Pantalla de Login con todo adentro de la tarjeta blanca"""
    aplicar_estilos_burbuja()

    _, col_centro, _ = st.columns([1, 1.25, 1])

    with col_centro:
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("form_login_burbuja", clear_on_submit=False):
            # Logo y títulos adentro del formulario para que queden sobre lo blanco
            if os.path.exists(ruta_logo):
                c1, c2, c3 = st.columns([1, 1, 1])
                with c2:
                    st.image(ruta_logo, width=120)

            st.markdown(
                '<p class="titulo-burbuja">AgriTechGO</p>', unsafe_allow_html=True
            )
            st.markdown(
                '<p class="subtitulo-burbuja">Acceso a la plataforma </p>',
                unsafe_allow_html=True,
            )

            email = st.text_input(
                "Correo o Usuario",
                placeholder="tucorreo@ejemplo.com",
                value=st.session_state.get("input_email", ""),
            )
            password = st.text_input(
                "Contraseña", type="password", placeholder="••••••••"
            )
            rol = st.selectbox(
                "Selecciona tu perfil en la plataforma:",
                [
                    " Agricultor / Caficultor",
                    " Comprador Directo",
                    " Inversionista Agro",
                    " Administradores (Equipo)",
                ],
            )

            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)

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
                st.error("Contraseña incorrecta. Usa `1234` o déjala libre.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("¿Usuario nuevo? Regístrate aquí", use_container_width=True):
            st.session_state.pantalla = "registro"
            st.rerun()


def mostrar_registro(ruta_logo):
    """Pantalla de Registro con todo adentro de la tarjeta blanca"""
    aplicar_estilos_burbuja()

    _, col_centro, _ = st.columns([1, 1.25, 1])

    with col_centro:
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("form_registro_burbuja", clear_on_submit=False):
            if os.path.exists(ruta_logo):
                c1, c2, c3 = st.columns([1, 1, 1])
                with c2:
                    st.image(ruta_logo, width=115)

            st.markdown(
                '<p class="titulo-burbuja">agriTechGO</p>', unsafe_allow_html=True
            )
            st.markdown(
                '<p class="subtitulo-burbuja">Crear una nueva cuenta</p>',
                unsafe_allow_html=True,
            )

            nombre_reg = st.text_input(
                "Nombre completo", placeholder="Tu nombre y apellido"
            )
            email_reg = st.text_input(
                "Correo electrónico", placeholder="tucorreo@ejemplo.com"
            )
            password_reg = st.text_input(
                "Contraseña", type="password", placeholder="••••••••"
            )
            confirm_reg = st.text_input(
                "Confirmar contraseña", type="password", placeholder="••••••••"
            )
            rol_reg = st.selectbox(
                "Selecciona tu perfil principal:",
                [
                    " Agricultor / Caficultor",
                    " Comprador Directo",
                    " Inversionista Agro",
                ],
            )

            st.markdown("<br>", unsafe_allow_html=True)
            submit_reg = st.form_submit_button(
                "Completar Registro", use_container_width=True
            )

        if submit_reg:
            if not nombre_reg.strip() or not email_reg.strip() or not password_reg:
                st.error("Por favor completa todos los campos obligatorios.")
            elif password_reg != confirm_reg:
                st.error("Las contraseñas no coinciden.")
            else:
                st.success("¡Cuenta creada con éxito! Ahora puedes iniciar sesión.")
                st.session_state.pantalla = "login"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("¿Ya tienes una cuenta? Ir al Login", use_container_width=True):
            st.session_state.pantalla = "login"
            st.rerun()