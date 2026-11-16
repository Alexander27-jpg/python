import streamlit as st
from datetime import date
from html import escape
from mysql.connector import Error as ErrorMySQL

from database.agricultor_db import (
    obtener_productor_demo,
    listar_cosechas,
    listar_fincas,
    leer_perfil,
    guardar_perfil,
    registrar_cosecha,
    actualizar_cosecha,
    publicar_proyecto,
    listar_proyectos_productor,
    listar_pedidos_agricultor,
    aceptar_pedido,
    rechazar_pedido,
)
import unicodedata

def comun_estado_cosecha(cosecha):
    """Calcula el estado usando cantidad y disponibilidad."""
    if cosecha["cantidad"] <= 0:
        return "Agotada"
    return "Disponible" if cosecha["activa"] else "Pausada"

def comun_listar_cosechas(agricultor_id=None, solo_disponibles=False):
    """Consulta cosechas persistentes en TiDB."""
    registros = listar_cosechas(
        agricultor_id=agricultor_id,
        solo_disponibles=solo_disponibles,
    )

    for registro in registros:
        registro["estado"] = comun_estado_cosecha(registro)

    return registros

def ejecutar_modo_agricultor():
    """Ejecuta el panel completo para el perfil de Agricultor / Caficultor"""

    def agri_pesos(valor):
        return "$" + f"{valor:,.0f}".replace(",", ".") + " COP"

    def agri_estado(cosecha):
        if cosecha["cantidad"] <= 0:
            return "Agotada"
        return "Disponible" if cosecha["activa"] else "Pausada"

    def agri_validar(finca, producto, cantidad, precio):
        errores = []
        if not finca.strip():
            errores.append("Escribe el nombre de la finca o lote.")
        if not producto.strip():
            errores.append("Escribe el nombre del producto.")
        if cantidad <= 0:
            errores.append("La cantidad debe ser mayor que cero.")
        if precio <= 0:
            errores.append("El precio debe ser mayor que cero.")
        return errores

    agri_usuario = str(st.session_state.get("usuario", "")).strip()

    if not agri_usuario:
        st.error("Ingresa primero con un usuario.")
        return

    try:
        agri_usuario_id = obtener_productor_demo(agri_usuario)
        agri_cosechas = comun_listar_cosechas(agri_usuario_id)
        agri_fincas_bd = listar_fincas(agri_usuario_id)
        agri_perfil = leer_perfil(agri_usuario_id)
    except (ErrorMySQL, ConnectionError, ValueError) as error:
        st.error("No se pudo cargar la información del productor.")
        if isinstance(error, ValueError):
            st.warning(str(error))
        elif isinstance(error, ErrorMySQL):
            st.caption(f"Código de base de datos: {error.errno}")
        return

    agri_aviso_key = f"agri_aviso_{agri_usuario_id}"

    #
    st.markdown(
        f"""
        <div style="
            background:#174B35;
            padding:28px;
            border-radius:18px;
            margin-bottom:20px;
        ">
            <div style="color:#D5E8B8;font-size:15px;">
                AGRITECHGO · AGRICULTOR / CAFICULTOR
            </div>
            <div style="
                color:#FFFFFF;
                font-size:34px;
                font-weight:750;
                margin:8px 0;
            ">
                Mi campo 🌱
            </div>
            <div style="color:#FFFFFF;font-size:17px;">
                Bienvenido, {escape(agri_usuario)}.
                Gestiona tus cosechas desde un solo lugar.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Tus registros se guardan en TiDB Cloud. "
        "La información se consulta al cargar o actualizar la vista."
    )

    agri_aviso = st.session_state.pop(agri_aviso_key, "")
    if agri_aviso:
        st.success(agri_aviso)

    agri_disponibles = sum(
        agri_estado(cosecha) == "Disponible"
        for cosecha in agri_cosechas
    )


    agri_col1, agri_col2, agri_col3 = st.columns(3)

    agri_col1.metric(
        "Cosechas registradas",
        len(agri_cosechas),
    )
    agri_col2.metric(
        "Cosechas disponibles",
        agri_disponibles,
    )
    agri_col3.metric(
        "Fincas / lotes",
        len(agri_fincas_bd),
    )

    st.markdown("---")

    
    # MENÚ LATERAL DEL AGRICULTOR
    st.sidebar.markdown("### 🌱 Menú Mi Campo")

    opcion_menu = st.sidebar.radio(
        "Navegación:",
        [
            "🌿 Mis cosechas",
            "➕ Registrar cosecha",
            "📦 Pedidos",
            "💰 Pagos",
            "👤 Mi perfil",
            "📈 Proyectos de inversión",
        ],
        key=f"agri_menu_{agri_usuario_id}",
    )

    # PERSONALIZACIÓN VISUAL DEL MENÚ
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            font-size: 17px !important;
            padding: 9px 8px !important;
            min-height: 38px;
            cursor: pointer;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] p {
            font-size: 17px !important;
            font-weight: 600 !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] {
            gap: 10px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # AYUDA SEGÚN LA SECCIÓN SELECCIONADA
    agri_ayudas_menu = {
        "🌿 Mis cosechas": "Consulta tus productos, cantidades y disponibilidad.",
        "➕ Registrar cosecha": "Registra los productos que tienes para vender.",
        "📦 Pedidos": "Revisa las solicitudes de compra que recibes.",
        "💰 Pagos": "Consulta la información de tus pagos.",
        "👤 Mi perfil": "Actualiza tus datos personales y los de tu finca.",
        "📈 Proyectos de inversión": "Publica necesidades de financiación para tu producción."
    }

    st.sidebar.markdown("---")
    st.sidebar.info(agri_ayudas_menu[opcion_menu])

    # SECCIÓN 1: MIS COSECHAS
    if opcion_menu == "🌿 Mis cosechas":
        st.subheader("🌿 Mis cosechas")
        st.write("Consulta tus productos, fotografías, precios y disponibilidad.")

        if not agri_cosechas:
            st.info("Aún no tienes cosechas registradas. Ingresa a Registrar cosecha para comenzar.")
        else:
            # BUSCADOR Y FILTRO EN UNA MISMA FILA
            col_busqueda, col_filtro, col_espacio = st.columns(
                [1.5, 1, 1],
                gap="medium"
            )

            with col_busqueda:
                agri_busqueda = st.text_input(
                    "Buscar producto o finca",
                    placeholder="Ejemplo: café o La Esperanza",
                    key=f"agri_busqueda_{agri_usuario}"
                )

            with col_filtro:
                agri_filtro = st.selectbox(
                    "Filtrar cosechas",
                    ["Todas", "Disponible", "Pausada", "Agotada"],
                    key=f"agri_filtro_{agri_usuario}"
                )


            def agri_normalizar_busqueda(texto):
                texto = unicodedata.normalize("NFD", str(texto).strip().casefold())
                return "".join(c for c in texto if unicodedata.category(c) != "Mn")

            agri_texto = agri_normalizar_busqueda(agri_busqueda)

            agri_visibles = [
                cosecha for cosecha in agri_cosechas
                if (agri_filtro == "Todas" or agri_estado(cosecha) == agri_filtro)
                and (
                    not agri_texto
                    or agri_texto in agri_normalizar_busqueda(cosecha["producto"])
                    or agri_texto in agri_normalizar_busqueda(cosecha["finca"])
                )
            ]

            st.caption(f"Mostrando {len(agri_visibles)} de {len(agri_cosechas)} cosechas")
            if not agri_visibles:
                st.info("No encontramos cosechas con esos filtros. Intenta otra búsqueda.")
                return

            # Carrusel de cosechas: dos tarjetas por página
            agri_pagina_key = f"agri_pagina_{agri_usuario_id}"

            agri_por_pagina = 2
            agri_total_paginas = (
                len(agri_visibles) + agri_por_pagina - 1
            ) // agri_por_pagina

            if agri_pagina_key not in st.session_state:
                st.session_state[agri_pagina_key] = 0

            # Evitar páginas inexistentes cuando cambia el filtro
            st.session_state[agri_pagina_key] = min(
                st.session_state[agri_pagina_key],
                max(0, agri_total_paginas - 1)
            )

            agri_pagina = st.session_state[agri_pagina_key]

            agri_inicio = agri_pagina * agri_por_pagina
            agri_fin = agri_inicio + agri_por_pagina

            agri_pagina_cosechas = agri_visibles[
                agri_inicio:agri_fin
            ]

            # Mostrar tarjetas en dos columnas
            agri_columnas = st.columns(2, gap="large")

            for indice, agri_c in enumerate(agri_pagina_cosechas):
                agri_id = agri_c["id"]
                agri_estado_actual = agri_estado(agri_c)

                with agri_columnas[indice]:
                    with st.container(border=True):

                        # Fotografía
                        if agri_c.get("foto"):
                            st.image(
                                agri_c["foto"],
                                use_container_width=True
                            )
                        else:
                            st.markdown(
                                """
                                <div style="
                                    background:#EAF3E8;
                                    border-radius:12px;
                                    height:150px;
                                    display:flex;
                                    align-items:center;
                                    justify-content:center;
                                    flex-direction:column;
                                    color:#24543B;
                                ">

                                    <div style="font-size:45px;">🌱</div>
                                    <b>Sin fotografía</b>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )


                        st.markdown(f"### {agri_c['producto']}")
                        st.caption(f"🏡 {agri_c['finca']}")

                        if agri_estado_actual == "Disponible":
                            st.success("● Disponible")
                        elif agri_estado_actual == "Pausada":
                            st.warning("● Publicación pausada")
                        else:
                            st.error("● Agotada")

                        st.markdown(
                            f"**{agri_pesos(agri_c['precio'])}**"
                        )
                        st.caption(
                            f"Precio por {agri_c['unidad']}"
                        )

                        st.metric(
                            "Cantidad disponible",
                            f"{agri_c['cantidad']:g} {agri_c['unidad']}"
                        )

                        st.caption(
                            f"Calidad / clasificación: "
                            f"{agri_c['calidad']}"
                        )

                        st.caption(
                            "📅 Cosecha: "
                            + agri_c["fecha"].strftime("%d/%m/%Y")
                        )

                        # Botón de edición más visible
                        st.markdown("---")

                        with st.expander(
                            "✏️ EDITAR INFORMACIÓN",
                            expanded=False
                        ):
                            with st.form(f"agri_editar_{agri_id}"):

                                agri_nueva_cantidad = st.number_input(
                                    "Cantidad disponible",
                                    min_value=0.0,
                                    value=float(agri_c["cantidad"]),
                                    step=1.0
                                )

                                agri_nuevo_precio = st.number_input(
                                    "Precio por unidad (COP)",
                                    min_value=1,
                                    value=int(agri_c["precio"]),
                                    step=100
                                )

                                agri_activa = st.checkbox(
                                    "Mantener disponible",
                                    value=agri_c["activa"]
                                )

                                agri_guardar = st.form_submit_button(
                                    "💾 Guardar cambios",
                                    use_container_width=True
                                )

                            if agri_guardar:
                                try:
                                    actualizar_cosecha(
                                        agri_usuario_id,
                                        agri_id,
                                        agri_nueva_cantidad,
                                        agri_nuevo_precio,
                                        agri_activa,
                                    )

                                except ValueError as error:
                                    st.error(str(error))

                                except (ErrorMySQL, ConnectionError):
                                    st.error(
                                        "No se pudo guardar el cambio en TiDB."
                                    )

                                else:
                                    st.session_state[agri_aviso_key] = (
                                        "Cosecha actualizada en la base de datos."
                                    )
                                    st.rerun()

            # Controles de navegación
            st.markdown("---")

            nav_izq, nav_centro, nav_der = st.columns(
                [1, 2, 1]
            )

            with nav_izq:
                if st.button(
                    "⬅ Anterior",
                    disabled=agri_pagina == 0,
                    use_container_width=True,
                    key=f"agri_anterior_{agri_usuario_id}"
                ):
                    st.session_state[agri_pagina_key] -= 1
                    st.rerun()

            with nav_centro:
                st.markdown(
                    f"<div style='text-align:center;padding:8px;'>"
                    f"<b>Página {agri_pagina + 1} de "
                    f"{agri_total_paginas}</b>"
                    f"</div>",
                    unsafe_allow_html=True
                )

            with nav_der:
                if st.button(
                    "Siguiente ➡",
                    disabled=agri_pagina >= agri_total_paginas - 1,
                    use_container_width=True,
                    key=f"agri_siguiente_{agri_usuario_id}"
                ):
                    st.session_state[agri_pagina_key] += 1
                    st.rerun()



    # SECCIÓN 2: REGISTRO DE COSECHA
    elif opcion_menu == "➕ Registrar cosecha":

        col_titulo_form, col_titulo_cosechas = st.columns(
            [1.5, 1],
            gap="large"
        )

        with col_titulo_form:
            st.subheader("➕ Registra tu cosecha")
            st.write(
                "Indica qué vendes, cuánto tienes disponible "
                "y el precio de cada unidad."
            )

        with col_titulo_cosechas:
            st.subheader("🌾 Tus cosechas")
            st.caption(
                "Selecciona una cosecha para consultar sus detalles."
            )

        col_formulario, col_vista = st.columns(
            [1.5, 1],
            gap="large"
        )


        with col_formulario:
            with st.form(f"agri_registro_{agri_usuario}"):
                agri_finca = st.text_input("Nombre del lote / finca", placeholder="Ejemplo: Finca La Esperanza", max_chars=100)
                agri_producto = st.text_input("Producto", placeholder="Ejemplo: Café pergamino, tomate o plátano", max_chars=80)
                
                agri_calidad = st.text_input(
                    "Calidad, variedad o clasificación (opcional)",
                    value="No aplica",
                    placeholder="Ejemplo: primera calidad, orgánico, variedad Hass",
                    max_chars=100,
                    help="Puedes indicar la clasificación de cualquier producto agrícola."
                )

                agri_unidad = st.selectbox("Unidad de venta", ["kg", "arroba", "unidad"])
                agri_cantidad = st.number_input("Cantidad disponible", min_value=0.0, value=0.0, step=1.0)
                agri_precio = st.number_input("Precio por unidad seleccionada (COP)", min_value=0, value=0, step=100)
                agri_fecha = st.date_input("Fecha de cosecha", value=date.today())
                agri_foto = st.file_uploader("Fotografía del producto", type=["png", "jpg", "jpeg", "webp"])

                agri_registrar = st.form_submit_button("🌱 Registrar cosecha", use_container_width=True)

            if agri_registrar:
                agri_errores = agri_validar(agri_finca, agri_producto, agri_cantidad, agri_precio)
                if agri_errores:
                    for agri_error in agri_errores:
                        st.error(agri_error)
                else:
                    try:
                        registrar_cosecha(
                            agri_usuario_id,
                            {
                                "finca": agri_finca,
                                "producto": agri_producto,
                                "calidad": agri_calidad,
                                "unidad": agri_unidad,
                                "cantidad": agri_cantidad,
                                "precio": agri_precio,
                                "fecha": agri_fecha,
                                "foto": (
                                    agri_foto.getvalue()
                                    if agri_foto is not None
                                    else None
                                ),
                            },
                        )
                    except ValueError as error:
                        st.error(str(error))
                    except (ErrorMySQL, ConnectionError):
                        st.error("No se pudo registrar la cosecha en TiDB.")
                    else:
                        st.session_state[agri_aviso_key] = (
                            "Finca y cosecha guardadas en TiDB Cloud."
                        )
                        st.rerun()

        
        with col_vista:
         if agri_cosechas:
            for cosecha_resumen in agri_cosechas:

                    nombre_producto = cosecha_resumen["producto"]
                    nombre_finca = cosecha_resumen["finca"]

                    with st.expander(
                        f"🌱 {nombre_producto} · 🏡 {nombre_finca}",
                        expanded=False
                    ):
                        st.markdown(f"**Producto:** {nombre_producto}")

                        st.markdown(
                            f"**Finca o lote:** {nombre_finca}"
                        )

                        st.markdown(
                            f"**Calidad o clasificación:** "
                            f"{cosecha_resumen['calidad']}"
                        )

                        st.markdown(
                            f"**Cantidad disponible:** "
                            f"{cosecha_resumen['cantidad']:g} "
                            f"{cosecha_resumen['unidad']}"
                        )

                        st.markdown(
                            f"**Precio por unidad:** "
                            f"{agri_pesos(cosecha_resumen['precio'])}"
                        )

                        st.markdown(
                            f"**Fecha de cosecha:** "
                            f"{cosecha_resumen['fecha'].strftime('%d/%m/%Y')}"
                        )

                        st.markdown(
                            f"**Estado:** "
                            f"{agri_estado(cosecha_resumen)}"
                        )

                        if cosecha_resumen.get("foto"):
                            st.image(
                                cosecha_resumen["foto"],
                                caption="Fotografía de tu cosecha",
                                use_container_width=True
                            )
                        else:
                            st.caption("📷 Esta cosecha no tiene fotografía.")

            else:
                st.info(
                    "Todavía no tienes cosechas registradas. "
                    "Cuando guardes tu primera cosecha aparecerá aquí."
                )

    
    # SECCIÓN 3: PEDIDOS
    elif opcion_menu == "📦 Pedidos":
        st.subheader("📦 Pedidos recibidos")
        st.write(
            "Consulta las solicitudes de compra de tus cosechas."
        )

        if st.button(
            "🔄 Actualizar pedidos",
            key=f"agri_actualizar_pedidos_{agri_usuario_id}",
        ):
            st.rerun()

        try:
            agri_pedidos = listar_pedidos_agricultor(
                agri_usuario_id
            )

            pendientes = [
                p for p in agri_pedidos
                if p["estado"] == "pendiente"
            ]

            aceptados = [
                p for p in agri_pedidos
                if p["estado"] == "aceptado"
            ]

            rechazados = [
                p for p in agri_pedidos
                if p["estado"] == "rechazado"
            ]

            met1, met2, met3 = st.columns(3)
            met1.metric("Pendientes", len(pendientes))
            met2.metric("Aceptados", len(aceptados))
            met3.metric("Rechazados", len(rechazados))

            st.markdown("---")

            if not agri_pedidos:
                st.info(
                    "Todavía no tienes solicitudes de compra."
                )

            for pedido in agri_pedidos:
                with st.container(border=True):
                    st.markdown(
                        f"### 📦 Pedido #{pedido['id']}"
                    )

                    st.caption(
                        f"Comprador: {pedido['comprador']} · "
                        f"Finca: {pedido['finca']}"
                    )

                    col1, col2 = st.columns(2)

                    col1.write(
                        f"**Producto:** {pedido['producto']}"
                    )
                    col1.write(
                        f"**Cantidad:** "
                        f"{pedido['cantidad']} {pedido['unidad']}"
                    )

                    col2.write(
                        f"**Precio unitario:** "
                        f"{agri_pesos(pedido['precio_unitario'])}"
                    )
                    col2.write(
                        f"**Total:** "
                        f"{agri_pesos(pedido['total'])}"
                    )

                    if pedido["estado"] == "pendiente":
                        st.warning("⏳ Pendiente de respuesta")

                        btn1, btn2 = st.columns(2)

                        if btn1.button(
                            "✅ Aceptar pedido",
                            key=f"agri_aceptar_{pedido['id']}",
                            use_container_width=True,
                        ):
                            try:
                                aceptar_pedido(
                                    agri_usuario_id,
                                    pedido["id"],
                                )
                            except ValueError as error:
                                st.error(str(error))
                            except ErrorMySQL as error:
                                st.error(
                                    "Error al aceptar el pedido. "
                                    f"Código: {error.errno}."
                                )
                            except ConnectionError:
                                st.error(
                                    "No se pudo conectar con TiDB."
                                )
                            else:
                                st.session_state[agri_aviso_key] = (
                                    f"Pedido #{pedido['id']} aceptado. "
                                    "Inventario actualizado correctamente."
                                )
                                st.rerun()

                        if btn2.button(
                            "❌ Rechazar pedido",
                            key=f"agri_rechazar_{pedido['id']}",
                            use_container_width=True,
                        ):
                            try:
                                rechazar_pedido(
                                    agri_usuario_id,
                                    pedido["id"],
                                )
                            except ValueError as error:
                                st.error(str(error))
                            except ErrorMySQL as error:
                                st.error(
                                    "Error al rechazar el pedido. "
                                    f"Código: {error.errno}."
                                )
                            except ConnectionError:
                                st.error(
                                    "No se pudo conectar con TiDB."
                                )
                            else:
                                st.session_state[agri_aviso_key] = (
                                    f"Pedido #{pedido['id']} rechazado."
                                )
                                st.rerun()

                    elif pedido["estado"] == "aceptado":
                        st.success(
                            "✅ Pedido aceptado. Inventario descontado."
                        )

                    elif pedido["estado"] == "rechazado":
                        st.error("❌ Pedido rechazado.")

                    elif pedido["estado"] == "entregado":
                        st.info("📦 Pedido entregado.")

                    elif pedido["estado"] == "cancelado":
                        st.info("Pedido cancelado.")

        except ErrorMySQL as error:
            st.error(
                "No se pudieron consultar los pedidos. "
                f"Código: {error.errno}."
            )
        except ConnectionError:
            st.error("No se pudo conectar con TiDB.")

    
    # SECCIÓN 4: PAGOS
    elif opcion_menu == "💰 Pagos":
        st.subheader("Mis pagos")
        st.info("Historial de pagos directos sin intermediarios.")
        st.write("Aquí podrás consultar los valores recibidos por tus ventas.")



    # SECCIÓN 5: PERFIL
    elif opcion_menu == "👤 Mi perfil":
        st.subheader("👤 Mi perfil de productor")
        st.write("Cuéntanos quién eres y dónde está tu finca.")

        st.caption("Usuario de acceso: " + agri_usuario)

        with st.form(f"agri_form_perfil_{agri_usuario}"):
            agri_nombre_perfil = st.text_input("Nombre del productor *", value=agri_perfil["nombre"], max_chars=100)
            agri_telefono_perfil = st.text_input("Celular de contacto", value=agri_perfil["telefono"], max_chars=25)
            agri_municipio_perfil = st.text_input("Municipio *", value=agri_perfil["municipio"], max_chars=80)
            agri_vereda_perfil = st.text_input("Vereda o sector", value=agri_perfil["vereda"], max_chars=100)
            agri_finca_perfil = st.text_input("Nombre de la finca principal *", value=agri_perfil["finca_principal"], max_chars=100)
            agri_descripcion_perfil = st.text_area("Acerca de tu actividad agrícola", value=agri_perfil["descripcion"], max_chars=600, height=120)

            agri_guardar_perfil = st.form_submit_button("Guardar mi perfil", use_container_width=True)

        if agri_guardar_perfil:
            agri_errores_perfil = []

            if not agri_nombre_perfil.strip():
                agri_errores_perfil.append("Escribe el nombre del productor.")
            if not agri_municipio_perfil.strip():
                agri_errores_perfil.append("Escribe el municipio.")
            if not agri_finca_perfil.strip():
                agri_errores_perfil.append("Escribe el nombre de la finca principal.")

            if agri_errores_perfil:
                for err in agri_errores_perfil:
                    st.error(err)
            else:
                try:
                    guardar_perfil(
                        agri_usuario_id,
                        {
                            "nombre": agri_nombre_perfil,
                            "telefono": agri_telefono_perfil,
                            "municipio": agri_municipio_perfil,
                            "vereda": agri_vereda_perfil,
                            "finca_principal": agri_finca_perfil,
                            "descripcion": agri_descripcion_perfil,
                        },
                    )
                except ValueError as error:
                    st.error(str(error))
                except ErrorMySQL as error:
                    if error.errno == 1062:
                        st.error(
                            "Ya tienes otra finca con ese nombre. "
                            "Utiliza un nombre diferente."
                        )
                    else:
                        st.error(
                            f"No se pudo guardar el perfil. "
                            f"Código: {error.errno}."
                        )
                except ConnectionError:
                    st.error("No se pudo conectar con TiDB.")
                else:
                    st.session_state[agri_aviso_key] = (
                        "Perfil y finca principal guardados en TiDB."
                    )
                    st.rerun()


    # SECCIÓN 6: PROYECTOS DE INVERSIÓN
    elif opcion_menu == "📈 Proyectos de inversión":
        st.subheader("📈 Proyectos de inversión")
        st.write(
            "Selecciona una finca y describe qué necesitas financiar."
        )
        st.info(
            "Los proyectos y aportes de esta versión son simulados. "
            "La rentabilidad indicada es una estimación del proyecto."
        )

        agri_fincas_activas = {
            finca["id"]: finca
            for finca in agri_fincas_bd
            if finca["activa"]
        }

        if not agri_fincas_activas:
            st.warning(
                "Primero registra una finca desde Mi perfil "
                "o Registrar cosecha."
            )
        else:
            with st.form(
                f"agri_publicar_proyecto_{agri_usuario_id}",
                clear_on_submit=False,
            ):
                proyecto_finca_id = st.selectbox(
                    "Finca donde se realizará el proyecto",
                    options=list(agri_fincas_activas),
                    format_func=lambda finca_id: (
                        agri_fincas_activas[finca_id]["nombre"]
                    ),
                )

                proyecto_titulo = st.text_input(
                    "Nombre del proyecto",
                    placeholder="Ejemplo: Instalación de riego por goteo",
                    max_chars=150,
                )

                proyecto_descripcion = st.text_area(
                    "¿Qué necesitas financiar y para qué?",
                    max_chars=2000,
                    height=120,
                )

                proyecto_meta = st.number_input(
                    "Meta de financiación (COP)",
                    min_value=0.0,
                    value=0.0,
                    step=100000.0,
                    format="%.2f",
                )

                proyecto_rentabilidad = st.number_input(
                    "Rentabilidad estimada del proyecto (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=0.5,
                    format="%.2f",
                    help=(
                        "Porcentaje estimado para el proyecto completo; "
                        "no es una tasa anual ni una ganancia garantizada."
                    ),
                )

                proyecto_riesgo = st.selectbox(
                    "Riesgo declarado del proyecto",
                    ["Bajo", "Medio", "Alto"],
                    index=1,
                )

                proyecto_ventas = st.number_input(
                    "Porcentaje de ventas destinado a inversionistas (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=1.0,
                    format="%.2f",
                    help=(
                        "Condición informativa de la simulación. "
                        "Todavía no genera repartos ni pagos automáticos."
                    ),
                )

                proyecto_publicar = st.form_submit_button(
                    "Publicar proyecto de simulación",
                    use_container_width=True,
                )

            if proyecto_publicar:
                try:
                    publicar_proyecto(
                        agri_usuario_id,
                        proyecto_finca_id,
                        {
                            "titulo": proyecto_titulo,
                            "descripcion": proyecto_descripcion,
                            "meta": proyecto_meta,
                            "rentabilidad_porcentaje": (
                                proyecto_rentabilidad
                            ),
                            "riesgo": proyecto_riesgo,
                            "porcentaje_ventas": proyecto_ventas,
                        },
                    )
                except ValueError as error:
                    st.error(str(error))
                except ErrorMySQL as error:
                    st.error(
                        "No se pudo publicar el proyecto. "
                        f"Código: {error.errno}."
                    )
                except ConnectionError:
                    st.error("No se pudo conectar con TiDB.")
                else:
                    st.session_state[agri_aviso_key] = (
                        "Proyecto guardado. Ya puede consultarse "
                        "al actualizar la vista Inversionista."
                    )
                    st.rerun()

        st.markdown("---")
        st.subheader("Mis proyectos publicados")

        if st.button(
            "🔄 Actualizar proyectos",
            key=f"agri_actualizar_proyectos_{agri_usuario_id}",
        ):
            st.rerun()

        try:
            agri_proyectos = listar_proyectos_productor(
                agri_usuario_id
            )
        except (ErrorMySQL, ConnectionError):
            st.error("No se pudieron consultar los proyectos.")
        else:
            if not agri_proyectos:
                st.info("Todavía no has publicado proyectos.")

            for proyecto in agri_proyectos:
                with st.container(border=True):
                    st.subheader(proyecto["titulo"])
                    st.caption(
                        f"Finca: {proyecto['finca']} · "
                        f"Estado: {proyecto['estado']}"
                    )
                    st.write(proyecto["descripcion"] or "")

                    col_meta, col_aportes = st.columns(2)
                    col_meta.metric(
                        "Meta",
                        agri_pesos(proyecto["meta"]),
                    )
                    col_aportes.metric(
                        "Aportes simulados",
                        agri_pesos(proyecto["recaudado"]),
                    )

                    progreso = (
                        float(
                            proyecto["recaudado"] / proyecto["meta"]
                        )
                        if proyecto["meta"] > 0
                        else 0.0
                    )

                    st.progress(
                        max(0.0, min(progreso, 1.0)),
                        text=f"Financiación: {progreso * 100:.1f}%",
                    )
                    