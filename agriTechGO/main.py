import streamlit as st
import os

# Configuración inicial de la página ancha
st.set_page_config(page_title="agriTechGO", page_icon="🌱", layout="wide")

# Nombre del archivo del logo en la raíz
RUTA_LOGO = "logo.png"

# Control de pantallas en la sesión
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "splash"

# -------------------------------------------------------------------------
# 1. PANTALLA DE CARGA (SPLASH SCREEN)
# -------------------------------------------------------------------------
if st.session_state.pantalla == "splash":
    # Importamos y llamamos la función del splash que pusiste en auth/login.py
    from auth.login import mostrar_splash
    mostrar_splash()

# -------------------------------------------------------------------------
# 2. PANTALLA DE LOGIN
# -------------------------------------------------------------------------
elif st.session_state.pantalla == "login":
    from auth.login import mostrar_login
    mostrar_login(RUTA_LOGO)

# -------------------------------------------------------------------------
# 3. PANTALLA DE REGISTRO
# -------------------------------------------------------------------------
elif st.session_state.pantalla == "registro":
    from auth.login import mostrar_registro
    mostrar_registro(RUTA_LOGO)

# -------------------------------------------------------------------------
# 4. PANTALLA DE DASHBOARD (SEGÚN EL ROL SELECCIONADO)
# -------------------------------------------------------------------------
elif st.session_state.pantalla == "dashboard":
    rol_actual = st.session_state.get("rol", "")
    
    # Botón flotante o en barra lateral para cerrar sesión
    if st.sidebar.button("⬅ Cerrar sesión y volver"):
        st.session_state.pantalla = "splash"
        st.rerun()

    # Redirigimos al archivo correspondiente dentro de la carpeta 'modos/'
    if "Agricultor" in rol_actual:
        from modos.agricultor import ejecutar_modo_agricultor
        ejecutar_modo_agricultor()
        
    elif "Comprador" in rol_actual:
        from modos.comprador import ejecutar_modo_comprador
        ejecutar_modo_comprador()
        
    elif "Inversionista" in rol_actual:
        from modos.inversionista import ejecutar_modo_inversionista
        ejecutar_modo_inversionista()
        
    elif "Administradores" in rol_actual:
        from modos.admin import ejecutar_modo_admin
        ejecutar_modo_admin()
    else:
        st.error("Rol no reconocido.")