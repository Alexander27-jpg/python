import streamlit as st

def cop(valor):
    """Formatea un número como pesos colombianos: $1.500.000 COP"""
    signo = "-" if valor < 0 else ""
    return f"{signo}${abs(valor):,.0f} COP".replace(",", ".")

def comun_estado_cosecha(cosecha):
    """Calcula el estado usando cantidad y disponibilidad."""
    if cosecha["cantidad"] <= 0:
        return "Agotada"
    return "Disponible" if cosecha["activa"] else "Pausada"

def comun_listar_cosechas(agricultor_id=None, solo_disponibles=False):
    """Consulta las cosechas registradas en la sesión actual."""
    resultados = []
    datos_agricultores = st.session_state.get("agri_datos", {})

    for propietario, datos in datos_agricultores.items():
        if agricultor_id is not None and propietario != agricultor_id:
            continue

        for cosecha in datos.get("cosechas", []):
            registro = dict(cosecha)
            registro["agricultor_id"] = propietario
            registro["estado"] = comun_estado_cosecha(registro)

            if solo_disponibles and registro["estado"] != "Disponible":
                continue

            resultados.append(registro)

    return resultados

def ejecutar_modo_comprador():
    """Ejecuta el panel interactivo del Comprador Directo"""
    st.title("🛒 Mercado de Café y Productos - agriTechGO")
    usuario_actual = st.session_state.get("usuario", "Comprador")
    st.success(f"Conectado como Comprador: **{usuario_actual}**")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Aliados Regionales", "Norte de Santander")
    col2.metric("Modelo", "Comercio Justo Directo")
    col3.metric("Ahorro Intermediarios", "15% - 20%")

    st.markdown("### 🌾 Lotes Disponibles de la Región (Cúcuta y Norte de Santander)")

    # Obtenemos las cosechas reales publicadas por los agricultores
    cosechas_disponibles = comun_listar_cosechas(solo_disponibles=True)

    if not cosechas_disponibles:
        st.info("⚠️ Aún no hay cosechas publicadas en la plataforma. ¡Registra una cosecha desde el perfil de Agricultor para verla aquí en tiempo real!")
    else:
        busqueda = st.text_input("🔍 Buscar producto, finca o variedad...", placeholder="Ej. Café, Finca El Mirador, Caturra...")
        
        if busqueda:
            cosechas_disponibles = [
                c for c in cosechas_disponibles 
                if busqueda.lower() in c['producto'].lower() or busqueda.lower() in c['finca'].lower()
            ]

        if not cosechas_disponibles:
            st.warning("No se encontraron productos que coincidan con tu búsqueda.")
        else:
            cols = st.columns(3)
            for idx, cosecha in enumerate(cosechas_disponibles):
                col_actual = cols[idx % 3]
                with col_actual:
                    with st.container(border=True):
                        st.markdown(f"#### 📦 {cosecha['producto']}")
                        st.caption(f"🏡 **{cosecha['finca']}**")
                        
                        if cosecha.get("foto"):
                            st.image(cosecha["foto"], use_container_width=True)
                        else:
                            st.markdown("""
                                <div style="background:#EAF3E8; border-radius:8px; height:120px; display:flex; align-items:center; justify-content:center; color:#24543B;">
                                    <b>🌱 Cosecha Local</b>
                                </div>
                            """, unsafe_allow_html=True)
                            
                        st.write(f"**Precio:** {cop(cosecha['precio'])} por {cosecha['unidad']}")
                        st.write(f"**Disponible:** {cosecha['cantidad']:g} {cosecha['unidad']}")
                        st.markdown(f"**Calidad:** {cosecha['calidad']}")
                        
                        if st.button(f"🛒 Comprar Lote", key=f"comprar_lote_{cosecha['id']}_{idx}"):
                            propietario_id = cosecha['agricultor_id']
                            cosechas_originales = st.session_state["agri_datos"][propietario_id]["cosechas"]
                            
                            compra_realizada = False
                            for orig in cosechas_originales:
                                if orig['id'] == cosecha['id']:
                                    if orig['cantidad'] > 0:
                                        orig['cantidad'] -= 1
                                        compra_realizada = True
                                    break
                                    
                            if compra_realizada:
                                st.success(f"¡Compra exitosa! Has adquirido {cosecha['producto']} de la **{cosecha['finca']}**.")
                                st.rerun()
                            else:
                                st.error("Lo sentimos, este lote ya se encuentra agotado.")

    st.markdown("---")
    if st.button("📦 Ver mis pedidos en tránsito"):
        st.info("No tienes pedidos en camino actualmente. ¡Selecciona un lote arriba para iniciar!")