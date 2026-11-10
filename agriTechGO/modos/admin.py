import streamlit as st

def ejecutar_modo_admin():
    """Ejecuta el panel de control y administración para el equipo"""
    st.title("⚙️ Panel de Control y Administración - agriTechGO")
    usuario_actual = st.session_state.get("usuario", "Alexander")
    st.success(f"Sesión de Administrador activa: **{usuario_actual}** - Equipo de Ingeniería")
    
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Usuarios Totales", "142")
    col2.metric("Transacciones", "38")
    col3.metric("Estado del Sistema", "Óptimo 🟢")
    col4.metric("Versión App", "v1.0.0 Pro")

    st.markdown("### 🛠️ Equipo de Desarrollo (Ingeniería de Sistemas)")
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