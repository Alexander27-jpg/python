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

    # ENCA
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

    (
        agri_tab1,
        agri_tab2,
        agri_tab3,
        agri_tab4,
        agri_tab5,
        agri_tab6,
    ) = st.tabs([
        "🌿 Mis cosechas",
        "➕ Registrar cosecha",
        "📦 Pedidos",
        "💰 Pagos",
        "👤 Mi perfil",
        "📈 Proyectos de inversión",
    ])

    # SECCIÓN 1: MIS COSECHAS
    with agri_tab1:
        st.subheader("🌿 Mis cosechas")
        st.write("Consulta tus productos, fotografías, precios y disponibilidad.")

        if not agri_cosechas:
            st.info("Aún no tienes cosechas registradas. Ingresa a Registrar cosecha para comenzar.")
        else:
            agri_busqueda = st.text_input(
                "Buscar por producto o finca",
                placeholder="Ejemplo: café o La Esperanza",
                key=f"agri_busqueda_{agri_usuario}"
            )

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

            for agri_c in agri_visibles:
                agri_id = agri_c["id"]
                agri_estado_actual = agri_estado(agri_c)

                with st.container(border=True):
                    agri_foto_col, agri_info_col = st.columns([1, 2], gap="large")

                    with agri_foto_col:
                        if agri_c.get("foto"):
                            st.image(agri_c["foto"], width=240)
                        else:
                            st.markdown(
                                """
                                <div style="
                                    background:#EAF3E8;
                                    border-radius:12px;
                                    min-height:180px;
                                    display:flex;
                                    align-items:center;
                                    justify-content:center;
                                    flex-direction:column;
                                    color:#24543B;
                                    text-align:center;
                                    padding:15px;
                                ">
                                    <div style="font-size:55px;">🌱</div>
                                    <b>Fotografía pendiente</b>
                                    <small>Agrega una imagen de tu producto</small>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    with agri_info_col:
                        st.markdown(f"### {agri_c['producto']}")
                        st.caption(f"🏡 {agri_c['finca']}")

                        if agri_estado_actual == "Disponible":
                            st.success("● Disponible")
                        elif agri_estado_actual == "Pausada":
                            st.warning("● Publicación pausada")
                        else:
                            st.error("● Agotada")

                        st.markdown(f"**{agri_pesos(agri_c['precio'])}**")
                        st.caption(f"Precio por {agri_c['unidad']}")

                        met1, met2 = st.columns(2)
                        met1.metric("Cantidad disponible", f"{agri_c['cantidad']:g} {agri_c['unidad']}")
                        met2.metric("Calidad", agri_c["calidad"])
                        st.caption("📅 Cosecha: " + agri_c["fecha"].strftime("%d/%m/%Y"))

                    with st.expander("✏️ Editar información"):
                        with st.form(f"agri_editar_{agri_id}"):
                            agri_nueva_cantidad = st.number_input(
                                "Cantidad disponible", min_value=0.0, value=float(agri_c["cantidad"]), step=1.0
                            )
                            agri_nuevo_precio = st.number_input(
                                "Precio por unidad (COP)", min_value=1, value=int(agri_c["precio"]), step=100
                            )
                            agri_activa = st.checkbox("Mantener disponible", value=agri_c["activa"])
                            agri_guardar = st.form_submit_button("Guardar cambios", use_container_width=True)

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

    # SECCIÓN 2: REGISTRO DE COSECHA
    with agri_tab2:
        st.subheader("Registra tu cosecha")
        st.write("Indica qué vendes, cuánto tienes disponible y el precio de cada unidad.")

        with st.form(f"agri_registro_{agri_usuario}"):
            agri_finca = st.text_input("Nombre del lote / finca", placeholder="Ejemplo: Finca La Esperanza", max_chars=100)
            agri_producto = st.text_input("Producto", placeholder="Ejemplo: Café pergamino, tomate o plátano", max_chars=80)
            agri_calidad = st.selectbox(
                "Calidad del grano — para café",
                ["No aplica", "Café Especial (Exóticas)", "Café Estándar Premium", "Café Comercial"]
            )
            agri_unidad = st.selectbox("Unidad de venta", ["kg", "arroba", "unidad"])
            agri_cantidad = st.number_input("Cantidad disponible", min_value=0.0, value=0.0, step=1.0)
            agri_precio = st.number_input("Precio por unidad seleccionada (COP)", min_value=0, value=0, step=100)
            agri_fecha = st.date_input("Fecha de cosecha", value=date.today())
            agri_foto = st.file_uploader("Fotografía del producto", type=["png", "jpg", "jpeg", "webp"])

            if agri_foto is not None:
                st.image(agri_foto, caption="Vista previa de tu producto", width=300)

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

    # SECCIÓN 3: PEDIDOS
    with agri_tab3:
        st.subheader("Mis pedidos")
        st.info("La recepción de pedidos está vinculada al módulo de transacciones.")
        st.write("Aquí aparecerán los compradores interesados en tus lotes publicados.")

    # SECCIÓN 4: PAGOS
    with agri_tab4:
        st.subheader("Mis pagos")
        st.info("Historial de pagos directos sin intermediarios.")
        st.write("Aquí podrás consultar los valores recibidos por tus ventas.")

    # SECCIÓN 5: PERFIL
    with agri_tab5:
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
    with agri_tab6:
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

print("Prueba ejecucion")



