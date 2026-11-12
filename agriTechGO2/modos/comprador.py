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
    """Consulta las cosechas registradas en la sesión actual por los agricultores."""
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
    
    # 1. Encabezado principal y bienvenida clara
    st.title("🛒 Comprar Alimentos del Campo")
    usuario_actual = st.session_state.get("usuario", "Comprador")
    st.success(f"Hola, **{usuario_actual}**. Aquí puedes comprar productos frescos directamente a los agricultores de la región.")
    
    st.markdown("---")
    
    # Métricas sencillas de impacto para la vista general
    col1, col2, col3 = st.columns(3)
    col1.metric("Región", "Norte de Santander")
    col2.metric("Modelo", "Comercio Justo")
    col3.metric("Intermediarios", "Cero")

    st.markdown("### 🌾 Lotes Disponibles en el Mercado")

    # 2. Obtenemos las cosechas reales publicadas en la sesión compartida
    cosechas_disponibles = comun_listar_cosechas(solo_disponibles=True)

    if not cosechas_disponibles:
        st.info("⚠️ Aún no hay cosechas publicadas en este momento. Pídele a tu compañero agricultor que registre una cosecha.")
    else:
        # 3. Buscador sencillo y amigable
        busqueda = st.text_input("🔍 Escribe el nombre del producto o finca que buscas:", placeholder="Ej. Café, Yuca, Finca El Mirador...")
        
        if busqueda:
            cosechas_disponibles = [
                c for c in cosechas_disponibles 
                if busqueda.lower() in c.get('producto', '').lower() or busqueda.lower() in c.get('finca', '').lower()
            ]

        if not cosechas_disponibles:
            st.warning("No encontramos productos que coincidan con tu búsqueda.")
        else:
            # 4. Diseño en tarjetas organizadas en filas de 3 columnas (Grid visual)
            cols = st.columns(3)
            for idx, cosecha in enumerate(cosechas_disponibles):
                col_actual = cols[idx % 3]
                with col_actual:
                    # Cada tarjeta se dibuja dentro de un contenedor con borde
                    with st.container(border=True):
                        st.subheader(f"📦 {cosecha.get('producto', 'Producto')}")
                        st.write(f"🏡 **Finca:** {cosecha.get('finca', 'N/D')}")
                        
                        # Mostrar imagen si fue cargada, o un recuadro representativo
                        if cosecha.get("foto"):
                            st.image(cosecha["foto"], use_container_width=True)
                        else:
                            st.markdown("""
                                <div style="background:#EAF3E8; border-radius:8px; height:100px; display:flex; align-items:center; justify-content:center; color:#24543B;">
                                    <b>🌱 Cosecha Local</b>
                                </div>
                            """, unsafe_allow_html=True)
                            
                        precio = cosecha.get('precio', 0)
                        unidad = cosecha.get('unidad', 'kg')
                        cantidad_disponible = cosecha.get('cantidad', 0)
                        
                        st.write(f"💰 **Precio:** {cop(precio)} por {unidad}")
                        st.write(f"📊 **Disponible:** {cantidad_disponible:g} {unidad}")
                        st.markdown(f"⭐ **Calidad:** {cosecha.get('calidad', 'Estándar')}")
                        
                        # 5. Selector numérico para que el usuario elija cuántas unidades llevar
                        cantidad_deseada = st.number_input(
                            f"¿Cuántos {unidad} deseas llevar?",
                            min_value=1.0,
                            max_value=float(cantidad_disponible),
                            value=1.0,
                            step=1.0,
                            key=f"cant_{cosecha['id']}_{idx}"
                        )
                        
                        # Cálculo del total en tiempo real para mayor transparencia
                        total_pagar = cantidad_deseada * precio
                        st.markdown(f"**Total a pagar:** {cop(total_pagar)}")
                        
                        # 6. Botón de compra que descuenta el inventario real del agricultor
                        if st.button(f"✅ Confirmar Compra", key=f"btn_comprar_{cosecha['id']}_{idx}"):
                            propietario_id = cosecha['agricultor_id']
                            cosechas_originales = st.session_state["agri_datos"][propietario_id]["cosechas"]
                            
                            compra_realizada = False
                            for orig in cosechas_originales:
                                if orig['id'] == cosecha['id']:
                                    if orig['cantidad'] >= cantidad_deseada:
                                        orig['cantidad'] -= cantidad_deseada
                                        compra_realizada = True
                                        if orig['cantidad'] == 0:
                                            orig['estado'] = 'Agotada'
                                    break
                                    
                            if compra_realizada:
                                st.success(f"¡Compra exitosa! Adquiriste {cantidad_deseada:g} {unidad} de {cosecha.get('producto')}.")
                                st.rerun() # Recarga la pantalla para actualizar el stock de inmediato
                            else:
                                st.error("No hay suficiente cantidad disponible en este lote.")

    st.markdown("---")
    if st.button("📦 Ver mis pedidos en tránsito"):
        st.info("No tienes pedidos en camino actualmente. ¡Selecciona un lote arriba para iniciar tu compra!")
          
# ejecutar
# py -m streamlit run main.py