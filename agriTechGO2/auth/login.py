import base64
import os
import random
import time
import streamlit as st
import sys

# Importamos tu función de conexión a la raíz
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
from conexion import obtener_conexion
from auth.email_sender import enviar_correo_bienvenida


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
    """Pantalla de Login exclusiva para admin con selección de perfil"""
    aplicar_estilos_burbuja()

    _, col_centro, _ = st.columns([1, 1.25, 1])

    with col_centro:
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("form_login_burbuja", clear_on_submit=False):
            # Centrado perfecto del logo con Flexbox dentro de la burbuja blanca
            if os.path.exists(ruta_logo):
                st.markdown(
                    '<div style="display: flex; justify-content: center; margin-bottom: 5px;">',
                    unsafe_allow_html=True,
                )
                st.image(ruta_logo, width=120)
                st.markdown("</div>", unsafe_allow_html=True)

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

            # Selector manual de perfil
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
            # Limpiamos espacios y convertimos a minúsculas obligatoriamente
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
    """Pantalla de recuperación de contraseña por código OTP vía Resend"""
    aplicar_estilos_burbuja()
    _, col_centro, _ = st.columns([1, 1.25, 1])

    with col_centro:
        with st.form("form_recuperar"):
            if os.path.exists(ruta_logo):
                st.markdown(
                    '<div style="display: flex; justify-content: center; margin-bottom: 5px;">',
                    unsafe_allow_html=True,
                )
                st.image(ruta_logo, width=100)
                st.markdown("</div>", unsafe_allow_html=True)

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
                            st.success(
                                "¡Código enviado! Revisa tu bandeja de entrada."
                            )
                            st.session_state.pantalla = "verificar_otp"
                            st.rerun()
                        else:
                            st.error(
                                "Este correo no está registrado en AgriTechGO."
                            )
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
            if os.path.exists(ruta_logo):
                st.markdown(
                    '<div style="display: flex; justify-content: center; margin-bottom: 5px;">',
                    unsafe_allow_html=True,
                )
                st.image(ruta_logo, width=100)
                st.markdown("</div>", unsafe_allow_html=True)

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
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("form_registro_burbuja", clear_on_submit=False):
            # Centrado perfecto del logo con Flexbox en el registro
            if os.path.exists(ruta_logo):
                st.markdown(
                    '<div style="display: flex; justify-content: center; margin-bottom: 5px;">',
                    unsafe_allow_html=True,
                )
                st.image(ruta_logo, width=115)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                '<p class="titulo-burbuja">agriTechGO</p>',
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