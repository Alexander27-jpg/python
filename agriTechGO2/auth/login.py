import base64
import os
import random
import sys
import time
import requests
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from auth.email_sender import enviar_correo_bienvenida
from conexion import obtener_conexion

# ==============================================================================
# RUTA DEL FONDO DEL PORTAL PRINCIPAL (Cámbiala aquí cuando tengas la nueva foto)
# ==============================================================================
FONDO_PORTAL = "ruta_logo.jpeg"


def obtener_base64(ruta_archivo):
    """Helper para convertir imágenes locales a base64 de forma segura"""
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def renderizar_logo_centrado(ruta_logo, ancho=120):
    """Renderiza el logo centrado en HTML/Base64 sin espacios extra ni botón de pantalla completa"""
    logo_b64 = obtener_base64(ruta_logo)
    if logo_b64:
        ext = os.path.splitext(ruta_logo)[1].lower().replace(".", "")
        if ext == "jpg":
            ext = "jpeg"
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; margin-bottom: 5px;">
                <img src="data:image/{ext};base64,{logo_b64}" width="{ancho}" style="border-radius: 50%;">
            </div>
            """,
            unsafe_allow_html=True,
        )


def mostrar_splash():
    """Muestra la pantalla de carga inicial"""
    video_base64 = obtener_base64("intro.mp4")

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
    st.session_state.pantalla = "landing"
    st.rerun()


@st.cache_data(ttl=3600)
def obtener_precios_publicos_agro():
    """Consulta la API abierta del DANE/SIPSA en datos.gov.co o usa respaldo local"""
    url_api = "https://www.datos.gov.co/resource/6287-236y.json?$limit=150&$order=fecha_captura DESC"

    respaldo = [
        {
            "producto": "Café Pergamino Seco (Carga)",
            "precio": "$2.213.250 COP",
            "mercado": "Referencia Nacional",
            "icono": "🌱",
        },
        {
            "producto": "Cacao Seco",
            "precio": "$28.400 COP/kg",
            "mercado": "Cúcuta / Cenabastos",
            "icono": "🍫",
        },
        {
            "producto": "Plátano Hartón Verde",
            "precio": "$1.850 COP/kg",
            "mercado": "Cúcuta / Cenabastos",
            "icono": "🍌",
        },
        {
            "producto": "Aguacate Hass",
            "precio": "$6.200 COP/kg",
            "mercado": "Referencia Nacional",
            "icono": "🥑",
        },
        {
            "producto": "Papa Pastusa",
            "precio": "$1.600 COP/kg",
            "mercado": "Cúcuta / Cenabastos",
            "icono": "🥔",
        },
        {
            "producto": "Tomate Chonto",
            "precio": "$2.900 COP/kg",
            "mercado": "Cúcuta / Cenabastos",
            "icono": "🍅",
        },
        {
            "producto": "Cebolla Cabezona Blanca",
            "precio": "$2.100 COP/kg",
            "mercado": "Cúcuta / Cenabastos",
            "icono": "🧅",
        },
        {
            "producto": "Yuca Chirosa",
            "precio": "$1.450 COP/kg",
            "mercado": "Cúcuta / Cenabastos",
            "icono": "🌿",
        },
        {
            "producto": "Limón Tahití",
            "precio": "$3.100 COP/kg",
            "mercado": "Referencia Nacional",
            "icono": "🍋",
        },
        {
            "producto": "Manzana Roja Importada",
            "precio": "$7.800 COP/kg",
            "mercado": "Cúcuta / Cenabastos",
            "icono": "🍎",
        },
    ]

    try:
        resp = requests.get(url_api, timeout=4)
        if resp.status_code == 200:
            datos = resp.json()
            productos_unicos = {}

            for fila in datos:
                nombre = fila.get("producto", "").strip().title()
                valor_raw = fila.get("precio_promedio_por_kilogramo") or fila.get("precio_promedio")
                ciudad = fila.get("ciudad", "Colombia").strip().title()

                if nombre and valor_raw and nombre not in productos_unicos:
                    try:
                        precio_num = float(valor_raw)
                        precio_fmt = f"${precio_num:,.0f} COP/kg".replace(",", ".")
                    except ValueError:
                        precio_fmt = f"${valor_raw} COP"

                    productos_unicos[nombre] = {
                        "producto": nombre,
                        "precio": precio_fmt,
                        "mercado": ciudad,
                        "icono": "🌾",
                    }

            lista_final = [respaldo[0]] + list(productos_unicos.values())
            if len(lista_final) > 5:
                return lista_final
    except Exception:
        pass

    return respaldo


def mostrar_landing(ruta_logo):
    """Portal de entrada estilo Agronet con datos públicos y sección corporativa"""
    if "tab_landing" not in st.session_state:
        st.session_state.tab_landing = "inicio"

    bg_base64 = obtener_base64(FONDO_PORTAL)
    logo_b64 = obtener_base64(ruta_logo)
    ext_logo = os.path.splitext(ruta_logo)[1].lower().replace(".", "")
    if ext_logo == "jpg":
        ext_logo = "jpeg"

    st.markdown(
        f"""
        <style>
            .block-container {{
                padding-top: 1rem !important;
                padding-bottom: 1rem !important;
                max-width: 100% !important;
            }}
            header[data-testid="stHeader"] {{
                display: none !important;
            }}
            .stApp {{
                background-image: linear-gradient(rgba(10, 30, 18, 0.55), rgba(10, 30, 18, 0.72)), url("data:image/jpeg;base64,{bg_base64}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            div.stButton > button {{
                background-color: transparent !important;
                color: #ffffff !important;
                border: 1.5px solid rgba(255, 255, 255, 0.7) !important;
                border-radius: 20px !important;
                font-weight: 700 !important;
                font-size: 0.9rem !important;
                padding: 0.35rem 1rem !important;
                transition: all 0.25s ease;
            }}
            div.stButton > button:hover {{
                background-color: #52b788 !important;
                border-color: #52b788 !important;
                color: #ffffff !important;
                transform: translateY(-2px);
            }}
            .indicador-card {{
                background: rgba(255, 255, 255, 0.13);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                padding: 18px 12px;
                text-align: center;
                color: white;
                transition: transform 0.2s;
                min-height: 155px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }}
            .indicador-card:hover {{
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.20);
            }}
            .indicador-icono {{
                font-size: 2rem;
                margin-bottom: 6px;
            }}
            .indicador-valor {{
                font-size: 1.3rem;
                font-weight: 800;
                color: #b7e4c7;
                margin-bottom: 4px;
            }}
            .indicador-titulo {{
                font-size: 0.9rem;
                font-weight: 700;
                color: #ffffff;
            }}
            .indicador-sub {{
                font-size: 0.75rem;
                color: #cbd5e1;
                margin-top: 3px;
            }}
            .negocio-box {{
                background: rgba(255, 255, 255, 0.95);
                color: #1b4332;
                border-radius: 20px;
                padding: 2.5rem;
                max-width: 950px;
                margin: 2rem auto;
                box-shadow: 0 20px 45px rgba(0,0,0,0.4);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- BARRA DE NAVEGACIÓN SUPERIOR ---
    col_brand, col_nav1, col_nav2, col_spacer, col_login, col_reg = st.columns(
        [2.2, 1.1, 1.4, 1.5, 1.3, 1.3]
    )

    with col_brand:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; padding-left: 15px;">
                <img src="data:image/{ext_logo};base64,{logo_b64}" width="44" style="border-radius: 50%; border: 2px solid #52b788;">
                <span style="font-size: 1.45rem; font-weight: 900; color: #ffffff; letter-spacing: 0.5px;">
                    AgriTech<span style="color: #52b788;">GO</span>
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_nav1:
        if st.button("Inicio", use_container_width=True):
            st.session_state.tab_landing = "inicio"
            st.rerun()

    with col_nav2:
        if st.button("Mi Negocio Agro", use_container_width=True):
            st.session_state.tab_landing = "negocio"
            st.rerun()

    with col_login:
        if st.button(" Iniciar Sesión", use_container_width=True):
            st.session_state.pantalla = "login"
            st.rerun()

    with col_reg:
        if st.button(" Registrarse", use_container_width=True):
            st.session_state.pantalla = "registro"
            st.rerun()

    st.markdown(
        "<hr style='border-color: rgba(255,255,255,0.2); margin-top: 8px; margin-bottom: 15px;'>",
        unsafe_allow_html=True,
    )

    # --- CONTENIDO DINÁMICO ---
    if st.session_state.tab_landing == "inicio":
        st.markdown(
            """
            <div style="text-align: center; padding: 5px 20px;">
                <p style="color: #b7e4c7; font-size: 0.9rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 6px;">
                    OBSERVATORIO DE PRECIOS MAYORISTAS (DATOS ABIERTOS COLOMBIA)
                </p>
                <h1 style="color: #ffffff; font-size: 3.4rem; font-weight: 900; line-height: 1.1; text-shadow: 0 4px 15px rgba(0,0,0,0.6); margin-bottom: 20px;">
                    Impulsando el progreso<br>del campo colombiano
                </h1>
            </div>
            """,
            unsafe_allow_html=True,
        )

        _, col_busq, _ = st.columns([1.2, 2.2, 1.2])
        with col_busq:
            busqueda = (
                st.text_input(
                    "Buscar producto",
                    placeholder=" Busca cualquier producto (ej: café, papa, manzana, tomate, yuca...)",
                    label_visibility="collapsed",
                )
                .strip()
                .lower()
            )

        st.markdown("<br>", unsafe_allow_html=True)

        catalogo_agro = obtener_precios_publicos_agro()

        if busqueda:
            filtrados = [
                p
                for p in catalogo_agro
                if busqueda in p["producto"].lower() or busqueda in p["mercado"].lower()
            ]

            if filtrados:
                mostrar = filtrados[:5]
                st.markdown(
                    f"<p style='text-align: center; color: #b7e4c7; font-weight: 600; margin-bottom: 15px;'>Mostrando {len(mostrar)} de {len(filtrados)} resultados encontrados:</p>",
                    unsafe_allow_html=True,
                )
                cols = st.columns(len(mostrar))
                for col, item in zip(cols, mostrar):
                    with col:
                        st.markdown(
                            f"""
                            <div class="indicador-card">
                                <div class="indicador-icono">{item['icono']}</div>
                                <div class="indicador-valor">{item['precio']}</div>
                                <div class="indicador-titulo">{item['producto']}</div>
                                <div class="indicador-sub">📍 {item['mercado']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            else:
                st.markdown(
                    f"""
                    <div style="text-align: center; background: rgba(0,0,0,0.65); padding: 20px; border-radius: 14px; max-width: 520px; margin: 0 auto; color: white;">
                        <p style="font-size: 1.1rem; font-weight: bold; color: #ffd166;">No encontramos "{busqueda}" en el boletín de hoy</p>
                        <p style="font-size: 0.9rem; color: #e2e8f0;">Inicia sesión o regístrate para publicar o solicitar cotizaciones directas con nuestros productores.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            destacados = catalogo_agro[:5]
            cols = st.columns(5)
            for col, item in zip(cols, destacados):
                with col:
                    st.markdown(
                        f"""
                        <div class="indicador-card">
                            <div class="indicador-icono">{item['icono']}</div>
                            <div class="indicador-valor">{item['precio']}</div>
                            <div class="indicador-titulo">{item['producto']}</div>
                            <div class="indicador-sub"> {item['mercado']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    elif st.session_state.tab_landing == "negocio":
        st.markdown(
            """
            <div class="negocio-box">
                <h2 style="color: #1b4332; font-weight: 900; margin-bottom: 10px;">
                     Sobre AgriTechGO - Mi Negocio Agro
                </h2>
                <p style="font-size: 1.05rem; color: #2d3748; line-height: 1.6;">
                    <strong>AgriTechGO</strong> es una plataforma tecnológica diseñada para transformar la comercialización agrícola en Colombia, eliminando las cadenas innecesarias de intermediación que reducen la rentabilidad de nuestros campesinos y caficultores.
                </p>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 25px;">
                    <div style="background: #f0fdf4; padding: 18px; border-radius: 14px; border-left: 5px solid #2d6a4f;">
                        <h4 style="color: #1b4332; margin-bottom: 8px;"> Agricultores / Caficultores</h4>
                        <p style="font-size: 0.9rem; color: #4a5568;">Publican sus cosechas directamente, fijan precios justos basados en el mercado real y gestionan sus lotes sin intermediarios.</p>
                    </div>
                    <div style="background: #f0fdf4; padding: 18px; border-radius: 14px; border-left: 5px solid #52b788;">
                        <h4 style="color: #1b4332; margin-bottom: 8px;"> Compradores Directos</h4>
                        <p style="font-size: 0.9rem; color: #4a5568;">Adquieren productos frescos, con trazabilidad garantizada y negociación transparente directamente desde la finca.</p>
                    </div>
                    <div style="background: #f0fdf4; padding: 18px; border-radius: 14px; border-left: 5px solid #1b4332;">
                        <h4 style="color: #1b4332; margin-bottom: 8px;"> Inversionistas Agro</h4>
                        <p style="font-size: 0.9rem; color: #4a5568;">Impulsan proyectos productivos del campo mediante financiamiento colaborativo con retornos claros y medibles.</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def aplicar_estilos_burbuja():
    """Estilos para la imagen de fondo y la tarjeta blanca centrada"""
    bg_base64 = obtener_base64(FONDO_PORTAL)

    st.markdown(
        f"""
        <style>
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_base64}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            [data-testid="stForm"] {{
                background-color: #ffffff !important;
                padding: 2rem 2.5rem !important;
                border-radius: 24px !important;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5) !important;
                border: none !important;
            }}
            [data-testid="stForm"] label p {{
                color: #1b4332 !important;
                font-weight: 700 !important;
                font-size: 0.95rem !important;
            }}
            .titulo-burbuja {{
                font-size: 1.8rem; font-weight: 800; color: #1b4332 !important;
                text-align: center; margin-bottom: 0px; margin-top: 5px;
            }}
            .subtitulo-burbuja {{
                font-size: 0.9rem; color: #4a5568 !important;
                text-align: center; margin-bottom: 15px;
            }}
            [data-testid="stFormSubmitButton"] > button {{
                background-color: #52b788 !important; color: white !important;
                border-radius: 12px !important; height: 45px !important;
                font-weight: bold !important; font-size: 1rem !important;
                border: none !important; box-shadow: 0 4px 12px rgba(82, 183, 136, 0.4);
            }}
            [data-testid="stFormSubmitButton"] > button:hover {{
                background-color: #40916c !important;
            }}
            div.stButton > button {{
                background-color: rgba(27, 67, 50, 0.85) !important;
                color: #ffffff !important;
                border-radius: 12px !important;
                height: 42px !important;
                font-weight: 600 !important;
                border: 1px solid rgba(82, 183, 136, 0.6) !important;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }}
            div.stButton > button:hover {{
                background-color: rgba(40, 95, 71, 0.95) !important;
                border-color: #52b788 !important;
                color: #ffffff !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def mostrar_login(ruta_logo):
    """Pantalla de Login exclusiva con selección de perfil"""
    aplicar_estilos_burbuja()

    _, col_centro, _ = st.columns([1, 1.25, 1])

    with col_centro:
        if st.button("← Volver al Portal Principal", use_container_width=True):
            st.session_state.pantalla = "landing"
            st.rerun()

        with st.form("form_login_burbuja", clear_on_submit=False):
            renderizar_logo_centrado(ruta_logo, ancho=120)

            st.markdown(
                '<p class="titulo-burbuja">AgriTechGO</p>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p class="subtitulo-burbuja">Acceso a la plataforma</p>',
                unsafe_allow_html=True,
            )

            email = st.text_input(
                "Usuario",
                placeholder="tucorreo@gmail.com",
                value=st.session_state.get("input_email", ""),
            )
            password = st.text_input(
                "Contraseña", type="password", placeholder="••••••••"
            )

            rol_elegido = st.selectbox(
                "Selecciona tu perfil en la plataforma:",
                [
                    "Agricultor / Caficultor",
                    "Comprador Directo",
                    "Inversionista Agro",
                    "Administradores (Equipo)",
                ],
            )

            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button(
                "Iniciar Sesión", use_container_width=True
            )

        if submit:
            usuario_ingresado = email.strip().lower()
            pass_ingresada = password.strip()

            if usuario_ingresado == "" or not pass_ingresada:
                st.error("Por favor completa todos los campos.")
            elif usuario_ingresado == "admin" and pass_ingresada == "admin1234":
                st.session_state["usuario"] = "admin"
                st.session_state["rol"] = rol_elegido
                st.session_state["pantalla"] = "dashboard"
                st.rerun()
            else:
                conexion = obtener_conexion()
                if conexion:
                    try:
                        cursor = conexion.cursor(dictionary=True)
                        cursor.execute(
                            "SELECT id, nombre, correo, rol, password_hash, activo FROM usuarios WHERE LOWER(correo) = %s",
                            (usuario_ingresado,),
                        )
                        user_db = cursor.fetchone()

                        if not user_db:
                            st.error("No existe una cuenta registrada con este correo.")
                        elif user_db["activo"] != 1:
                            st.error("Esta cuenta se encuentra inactiva.")
                        elif user_db["password_hash"] != pass_ingresada:
                            st.error("Contraseña incorrecta.")
                        elif rol_elegido not in user_db["rol"]:
                            st.warning(
                                f"Tu cuenta no tiene habilitado el perfil '{rol_elegido}'. "
                                f"Tus perfiles registrados son: {user_db['rol']}"
                            )
                        else:
                            st.session_state["usuario_id"] = user_db["id"]
                            st.session_state["usuario"] = user_db["nombre"]
                            st.session_state["correo"] = user_db["correo"]
                            st.session_state["rol"] = rol_elegido
                            st.session_state["pantalla"] = "dashboard"
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error al consultar la base de datos: {e}")
                    finally:
                        cursor.close()
                        conexion.close()
                else:
                    st.error("No se pudo conectar a la base de datos de TiDB Cloud.")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("¿Olvidaste tu contraseña?", use_container_width=True):
            st.session_state.pantalla = "recuperar"
            st.rerun()

        if st.button("¿Usuario nuevo? Regístrate aquí", use_container_width=True):
            st.session_state.pantalla = "registro"
            st.rerun()


def mostrar_recuperar_password(ruta_logo):
    """Pantalla de recuperación de contraseña por código OTP"""
    aplicar_estilos_burbuja()
    _, col_centro, _ = st.columns([1, 1.25, 1])

    with col_centro:
        with st.form("form_recuperar"):
            renderizar_logo_centrado(ruta_logo, ancho=100)

            st.markdown(
                '<p class="titulo-burbuja">Recuperar Clave</p>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p class="subtitulo-burbuja">Te enviaremos un código de verificación</p>',
                unsafe_allow_html=True,
            )

            email_rec = st.text_input(
                "Correo electrónico registrado",
                placeholder="tucorreo@ejemplo.com",
            )
            submit_rec = st.form_submit_button(
                "Enviar Código", use_container_width=True
            )

        if submit_rec:
            if not email_rec.strip():
                st.error("Ingresa un correo válido.")
            else:
                conexion = obtener_conexion()
                if conexion:
                    try:
                        cursor = conexion.cursor(dictionary=True)
                        cursor.execute(
                            "SELECT nombre FROM usuarios WHERE correo = %s",
                            (email_rec.strip(),),
                        )
                        user_data = cursor.fetchone()

                        if user_data:
                            codigo = str(random.randint(100000, 999900))
                            st.session_state["codigo_otp"] = codigo
                            st.session_state["email_otp"] = email_rec.strip()

                            enviar_correo_bienvenida(
                                correo_destino=email_rec.strip(),
                                nombre_usuario=user_data["nombre"],
                                roles_usuario=f"Tu código de recuperación es: {codigo}",
                            )
                            st.success("¡Código enviado! Revisa tu bandeja de entrada.")
                            st.session_state.pantalla = "verificar_otp"
                            st.rerun()
                        else:
                            st.error("Este correo no está registrado en AgriTechGO.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        cursor.close()
                        conexion.close()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Volver al Login", use_container_width=True):
            st.session_state.pantalla = "login"
            st.rerun()


def mostrar_verificar_otp(ruta_logo):
    """Pantalla para introducir el código OTP y cambiar la contraseña"""
    aplicar_estilos_burbuja()
    _, col_centro, _ = st.columns([1, 1.25, 1])

    with col_centro:
        with st.form("form_otp"):
            renderizar_logo_centrado(ruta_logo, ancho=100)

            st.markdown(
                '<p class="titulo-burbuja">Verificar Código</p>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p class="subtitulo-burbuja">Introduce el código de 6 dígitos enviado a tu correo y tu nueva contraseña</p>',
                unsafe_allow_html=True,
            )

            ingresado_otp = st.text_input("Código de verificación")
            nueva_pass = st.text_input(
                "Nueva contraseña", type="password", placeholder="••••••••"
            )
            submit_otp = st.form_submit_button(
                "Actualizar Contraseña", use_container_width=True
            )

        if submit_otp:
            if ingresado_otp == st.session_state.get("codigo_otp"):
                conexion = obtener_conexion()
                if conexion:
                    try:
                        cursor = conexion.cursor()
                        query = "UPDATE usuarios SET password_hash = %s WHERE correo = %s"
                        cursor.execute(
                            query,
                            (
                                nueva_pass,
                                st.session_state.get("email_otp"),
                            ),
                        )
                        conexion.commit()
                        st.success(
                            "¡Contraseña actualizada con éxito! Ya puedes iniciar sesión."
                        )
                        st.session_state.pantalla = "login"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al actualizar: {e}")
                    finally:
                        cursor.close()
                        conexion.close()
            else:
                st.error("El código de verificación es incorrecto.")


def mostrar_registro(ruta_logo):
    """Pantalla de Registro con selección múltiple de roles"""
    aplicar_estilos_burbuja()

    _, col_centro, _ = st.columns([1, 1.25, 1])

    with col_centro:
        if st.button("← Volver al Portal Principal", use_container_width=True):
            st.session_state.pantalla = "landing"
            st.rerun()

        with st.form("form_registro_burbuja", clear_on_submit=False):
            renderizar_logo_centrado(ruta_logo, ancho=115)

            st.markdown(
                '<p class="titulo-burbuja">AgriTechGO</p>',
                unsafe_allow_html=True,
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

            st.markdown(
                "<p style='color: #1b4332; font-weight: 700; font-size: 0.95rem;"
                " margin-bottom: 5px;'>Selecciona tus roles (puedes elegir"
                " varios):</p>",
                unsafe_allow_html=True,
            )

            es_agricultor = st.checkbox("Agricultor / Caficultor")
            es_comprador = st.checkbox("Comprador Directo")
            es_inversionista = st.checkbox("Inversionista Agro")

            st.markdown("<br>", unsafe_allow_html=True)
            submit_reg = st.form_submit_button(
                "Completar Registro", use_container_width=True
            )

        if submit_reg:
            roles_seleccionados = []
            if es_agricultor:
                roles_seleccionados.append("Agricultor / Caficultor")
            if es_comprador:
                roles_seleccionados.append("Comprador Directo")
            if es_inversionista:
                roles_seleccionados.append("Inversionista Agro")

            if not nombre_reg.strip() or not email_reg.strip() or not password_reg:
                st.error("Por favor completa todos los campos obligatorios.")
            elif not roles_seleccionados:
                st.error("Debes seleccionar al menos un rol en la plataforma.")
            elif password_reg != confirm_reg:
                st.error("Las contraseñas no coinciden.")
            else:
                rol_final = ", ".join(roles_seleccionados)

                conexion = obtener_conexion()
                if conexion:
                    try:
                        cursor = conexion.cursor()
                        query = "INSERT INTO usuarios (nombre, correo, rol, password_hash, activo) VALUES (%s, %s, %s, %s, 1)"
                        cursor.execute(
                            query,
                            (
                                nombre_reg.strip(),
                                email_reg.strip(),
                                rol_final,
                                password_reg,
                            ),
                        )
                        conexion.commit()

                        try:
                            enviar_correo_bienvenida(
                                correo_destino=email_reg.strip(),
                                nombre_usuario=nombre_reg.strip(),
                                roles_usuario=rol_final,
                            )
                        except Exception as mail_err:
                            print(
                                f"Advertencia: No se pudo enviar el correo: {mail_err}"
                            )

                        st.success(
                            "¡Cuenta creada con éxito! Roles guardados: "
                            f"{rol_final}. Ahora puedes iniciar sesión."
                        )
                        st.session_state.pantalla = "login"
                        st.rerun()
                    except Exception as e:
                        st.error(
                            f"Error al registrar el usuario en la base de datos: {e}"
                        )
                    finally:
                        cursor.close()
                        conexion.close()
                else:
                    st.error("No se pudo conectar a la base de datos de TiDB Cloud.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("¿Ya tienes una cuenta? Ir al Login", use_container_width=True):
            st.session_state.pantalla = "login"
            st.rerun()