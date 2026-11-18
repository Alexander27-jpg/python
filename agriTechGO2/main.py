import os
import streamlit as st

# Configuración inicial de la página
st.set_page_config(
    page_title="AgriTechGO",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 1. IMPORTAR EL CHATBOT (Como lo dejaste en la raíz, se importa directo)
from chatbot import renderizar_chatbot

# Importar los módulos de autenticación y modos (incluyendo mostrar_landing)
from auth.login import (
    mostrar_landing,
    mostrar_login,
    mostrar_recuperar_password,
    mostrar_registro,
    mostrar_splash,
    mostrar_verificar_otp,
)
from modos.admin import ejecutar_modo_admin
from modos.agricultor import ejecutar_modo_agricultor
from modos.comprador import ejecutar_modo_comprador
from modos.inversionista import ejecutar_modo_inversionista

# Definir la ruta del logo
RUTA_LOGO = "logo.png"

# Inicializar las variables de sesión globales si no existen
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "splash"

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

if "rol" not in st.session_state:
    st.session_state.rol = ""


# Controlador principal de pantallas
def main():
    pantalla_actual = st.session_state.get("pantalla", "splash")

    if pantalla_actual == "splash":
        mostrar_splash()

    elif pantalla_actual == "landing":
        mostrar_landing(RUTA_LOGO)

    elif pantalla_actual == "login":
        mostrar_login(RUTA_LOGO)

    elif pantalla_actual == "registro":
        mostrar_registro(RUTA_LOGO)

    elif pantalla_actual == "recuperar":
        mostrar_recuperar_password(RUTA_LOGO)

    elif pantalla_actual == "verificar_otp":
        mostrar_verificar_otp(RUTA_LOGO)

    elif pantalla_actual == "dashboard":
        # Botón superior para cerrar sesión (integrado sin conflictos)
        col_espacio, col_btn = st.columns([8, 2])
        with col_btn:
            if st.button("🚪 Cerrar Sesión", key="cerrar_sesion_dash", use_container_width=True):
                st.session_state.pantalla = "landing"  # Vuelve al portal principal al cerrar sesión
                st.session_state.usuario = ""
                st.session_state.rol = ""
                st.rerun()

        rol_activo = st.session_state.get("rol", "")

        # Enrutar según el rol seleccionado al iniciar sesión
        if "Agricultor" in rol_activo:
            ejecutar_modo_agricultor()
        elif "Comprador" in rol_activo:
            ejecutar_modo_comprador()
        elif "Inversionista" in rol_activo:
            ejecutar_modo_inversionista()
        elif "Administradores" in rol_activo:
            ejecutar_modo_admin()
        else:
            # Fallback por defecto si el rol no coincide
            ejecutar_modo_agricultor()

    # 2. LLAMAR AL CHATBOT GLOBAL (Aparece en toda la app menos en el splash)
    if pantalla_actual != "splash":
        renderizar_chatbot()


if __name__ == "__main__":
    main()