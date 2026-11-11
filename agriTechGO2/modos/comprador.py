import streamlit as st

def cop(valor):
    """Formatea un número como pesos colombianos: $1.500.000 COP"""
    signo = "-" if valor < 0 else ""
    return f"{signo}${abs(valor):,.0f} COP".replace(",", ".")

def comun_estado_cosecha(cosecha):
    """Calcula el estado usando cantidad y disponibilidad."""
    if cosecha["cantidad"] <= 0:
        return "Agotada"
    return "Disponible" if cosecha.get("activa", True) else "Pausada"

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
                if busqueda.lower() in c.get('producto', '').lower() or busqueda.lower() in c.get('finca', '').lower()
            ]

        if not cosechas_disponibles:
            st.warning("No se encontraron productos que coincidan con tu búsqueda.")
        else:
            # Mostrar en tarjetas organizadas en filas de 3 columnas (Grid visual)
            cols = st.columns(3)
            for idx, cosecha in enumerate(cosechas_disponibles):
                col_actual = cols[idx % 3]
                with col_actual:
                    with st.container(border=True):
                        st.markdown(f"#### 📦 {cosecha.get('producto', 'Producto')}")
                        st.caption(f"🏡 **{cosecha.get('finca', 'N/D')}**")
                        
                        if cosecha.get("foto"):
                            st.image(cosecha["foto"], use_container_width=True)
                        else:
                            st.markdown("""
                                <div style="background:#EAF3E8; border-radius:8px; height:120px; display:flex; align-items:center; justify-content:center; color:#24543B;">
                                    <b>🌱 Cosecha Local</b>
                                </div>
                            """, unsafe_allow_html=True)
                            
                        precio = cosecha.get('precio', 0)
                        unidad = cosecha.get('unidad', 'kg')
                        cantidad_disponible = cosecha.get('cantidad', 0)
                        
                        st.write(f"**Precio:** {cop(precio)} por {unidad}")
                        st.write(f"**Disponible:** {cantidad_disponible:g} {unidad}")
                        st.markdown(f"**Calidad:** {cosecha.get('calidad', 'Estándar')}")
                        
                        # Selector de cantidad que el comprador desea adquirir
                        cantidad_a_comprar = st.number_input(
                            f"Cantidad a comprar ({unidad}):",
                            min_value=1.0,
                            max_value=float(cantidad_disponible),
                            value=1.0,
                            step=1.0,
                            key=f"cant_{cosecha['id']}_{idx}"
                        )
                        
                        # Mostrar el precio total calculado en tiempo real
                        precio_total = cantidad_a_comprar * precio
                        st.info(f"**Total a pagar:** {cop(precio_total)}")
                        
                        # Botón interactivo conectado con la lógica de inventario real
                        if st.button(f"🛒 Comprar {cantidad_a_comprar:g} {unidad}", key=f"comprar_lote_{cosecha['id']}_{idx}"):
                            propietario_id = cosecha['agricultor_id']
                            cosechas_originales = st.session_state["agri_datos"][propietario_id]["cosechas"]
                            
                            compra_realizada = False
                            for orig in cosechas_originales:
                                if orig['id'] == cosecha['id']:
                                    if orig['cantidad'] >= cantidad_a_comprar:
                                        orig['cantidad'] -= cantidad_a_comprar
                                        compra_realizada = True
                                        if orig['cantidad'] == 0:
                                            orig['estado'] = 'Agotada'
                                    break
                                    
                            if compra_realizada:
                                st.success(f"¡Compra exitosa! Adquiriste {cantidad_a_comprar:g} {unidad} de {cosecha.get('producto')} de la **{cosecha.get('finca')}**.")
                                st.rerun()
                            else:
                                st.error("No hay suficiente cantidad disponible en este lote.")

    st.markdown("---")
    if st.button("📦 Ver mis pedidos en tránsito"):
        st.info("No tienes pedidos en camino actualmente. ¡Selecciona un lote arriba para iniciar!")
          
# ejecutar
# py -m streamlit run main.py