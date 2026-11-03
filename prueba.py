import streamlit as st

# 1. Definimos cuál es la pantalla inicial si la app apenas está abriendo
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "pantalla_1"

# ----------------------------------------------------
# PANTALLA 1
# ----------------------------------------------------
if st.session_state.pantalla == "pantalla_1":
    st.title("📱 Primera Pantalla")
    st.write("Esta es la pantalla de inicio.")

    # Al tocar este botón, cambiamos la variable a 'pantalla_2'
    if st.button("Ir a la segunda pantalla ➔"):
        st.session_state.pantalla = "pantalla_2"
        st.rerun()  # Recarga la app para mostrar el cambio al instante

# ----------------------------------------------------
# PANTALLA 2
# ----------------------------------------------------
elif st.session_state.pantalla == "pantalla_2":
    st.title("🎉 ¡Llegaste a la Segunda Pantalla!")
    st.write("Acá ya estás en otro módulo totalmente diferente.")

    # Botón para volver
    if st.button("⬅ Volver a la primera pantalla"):
        st.session_state.pantalla = "pantalla_1"
        st.rerun()

    