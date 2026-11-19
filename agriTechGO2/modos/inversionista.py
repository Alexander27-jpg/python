import base64
import unicodedata
from html import escape
from pathlib import Path

import streamlit as st
from mysql.connector import Error as ErrorMySQL

from database.inversionista_db import (
    iniciar_inversionista,
    cargar_datos,
    guardar_perfil,
    guardar_foto,
    cambiar_seguimiento,
    mover_wallet,
    invertir,
)
from database.reparto_db import (
    total_rendimientos,
    porcentajes_por_proyecto,
    listar_repartos_inversionista,
)


def cop(valor):

    signo = "-" if valor < 0 else ""
    return f"{signo}${abs(valor):,.0f} COP".replace(",", ".")


def inv_normalizar(texto):
    """Minúsculas y sin tildes, para que las búsquedas sean más flexibles."""
    texto = unicodedata.normalize("NFD", str(texto or "").strip().casefold())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def mostrar_error(error):
    if isinstance(error, ValueError):
        st.error(str(error))
    elif isinstance(error, ErrorMySQL):
        st.error(f"No se pudo completar la operación. Código: {error.errno}.")
    else:
        st.error("No se pudo conectar con TiDB.")


def ejecutar_accion(usuario_id, mensaje, funcion, *argumentos):
    try:
        funcion(*argumentos)
    except (ValueError, ErrorMySQL, ConnectionError) as error:
        mostrar_error(error)
    else:
        st.session_state[f"inv_aviso_{usuario_id}"] = mensaje
        st.rerun()


def inv_tab_perfil(usuario_id, datos):
    perfil = datos["perfil"]
    st.subheader("👤 Mi perfil de inversionista")
    st.write("Cuéntanos quién eres y qué te interesa financiar.")
    st.caption("Usuario de acceso: " + str(st.session_state.get("usuario", "")))

    col_foto, col_datos = st.columns([1, 2])

    with col_foto:
        if perfil["foto"]:
            st.image(perfil["foto"], width="stretch")
        else:
            st.info("Aún no tienes foto de perfil.")

        archivo = st.file_uploader(
            "Subir foto — máximo 2 MB",
            type=["png", "jpg", "jpeg"],
            key=f"inv_foto_{usuario_id}",
        )

        if st.button("📷 Guardar foto"):
            if archivo is None:
                st.warning("Selecciona primero una foto.")
            else:
                ejecutar_accion(
                    usuario_id,
                    "Foto guardada en TiDB.",
                    guardar_foto,
                    usuario_id,
                    archivo.getvalue(),
                )

    with col_datos:
        with st.form(f"inv_perfil_{usuario_id}"):
            nombre = st.text_input(
                "Nombre a mostrar",
                value=perfil["nombre"] or "",
                max_chars=100,
            )
            descripcion = st.text_area(
                "Descripción",
                value=perfil["descripcion"],
                max_chars=600,
                height=150,
            )
            guardar = st.form_submit_button("💾 Guardar perfil", width="stretch")

        if guardar:
            ejecutar_accion(
                usuario_id,
                "Perfil guardado en TiDB.",
                guardar_perfil,
                usuario_id,
                nombre,
                descripcion,
            )

    st.markdown("---")
    st.write(perfil["nombre"])
    st.write(perfil["descripcion"] or "Sin descripción todavía.")


def inv_tab_fincas(usuario_id, datos):
    st.subheader("🌱 Fincas y proyectos")
    st.write("Sigue fincas y revisa los proyectos que puedes financiar.")

    if st.button(
        "🔄 Actualizar proyectos",
        key=f"inv_actualizar_proyectos_{usuario_id}",
    ):
        st.rerun()

    if not datos["fincas"]:
        st.info("Todavía no hay fincas publicadas.")
        return

    # BUSCADOR Y FILTRO EN UNA MISMA FILA
    col_busqueda, col_filtro, col_espacio = st.columns([1.5, 1, 1], gap="medium")

    with col_busqueda:
        busqueda = st.text_input(
            "Buscar finca o productor",
            placeholder="Ejemplo: La Esperanza o Aurelio",
            key=f"inv_busqueda_{usuario_id}",
        )

    with col_filtro:
        filtro = st.selectbox(
            "Filtrar fincas",
            ["Todas", "Solo las que sigo"],
            key=f"inv_filtro_{usuario_id}",
        )

    texto = inv_normalizar(busqueda)

    fincas = [
        finca for finca in datos["fincas"]
        if (filtro == "Todas" or finca["id"] in datos["siguiendo"])
        and (
            not texto
            or texto in inv_normalizar(finca["nombre"])
            or texto in inv_normalizar(finca["agricultor"])
        )
    ]

    st.caption(f"Mostrando {len(fincas)} de {len(datos['fincas'])} fincas")

    if not fincas:
        st.info("No encontramos fincas con esos filtros. Intenta otra búsqueda.")
        return

    # ---- PEGA AQUÍ ----
    try:
        porcentajes = porcentajes_por_proyecto([p["id"] for p in datos["proyectos"]])
    except (ErrorMySQL, ConnectionError):
        porcentajes = {}
    # -------------------

    for finca in fincas:
        with st.container(border=True, key=f"inv_tarjeta_{finca['id']}"):
            c1, c2 = st.columns([3, 1])
            c1.subheader(finca["nombre"])

            ubicacion = " · ".join(
                parte for parte in (finca["municipio"], finca["vereda"])
                if parte
            )
            c1.caption(
                f"Productor: {finca['agricultor']} | "
                f"Ubicación: {ubicacion or 'Sin registrar'}"
            )

            siguiendo = finca["id"] in datos["siguiendo"]
            if c2.button(
                "⭐ Dejar de seguir" if siguiendo else "☆ Seguir",
                key=f"inv_seguir_{usuario_id}_{finca['id']}",
            ):
                ejecutar_accion(
                    usuario_id,
                    "Seguimiento actualizado.",
                    cambiar_seguimiento,
                    usuario_id,
                    finca["id"],
                    not siguiendo,
                )

            proyectos = [
                proyecto for proyecto in datos["proyectos"]
                if proyecto["finca_id"] == finca["id"]
            ]

            if not proyectos:
                st.info("Esta finca todavía no tiene proyectos publicados.")

            for proyecto in proyectos:
                st.markdown("---")
                st.write(f"**Proyecto: {proyecto['titulo']}**")
                st.write(proyecto["descripcion"] or "")
                st.caption("Proyecto de simulación. No se mueve dinero real.")


                pct = porcentajes.get(proyecto["id"])
                if pct:
                    st.info(
                        f"El agricultor destina el {pct:g}% de las ventas de esta finca "
                        "a los inversionistas de este proyecto, en proporción a lo que aporte cada uno."
                    )

                m1, m2, m3 = st.columns(3)
                m1.metric(
                    "Rentabilidad estimada del proyecto",
                    f"{proyecto['rentabilidad_estimada'] * 100:.1f}%",
                )
                m2.metric("Riesgo declarado", proyecto["riesgo"])
                m3.metric("Avance", f"{proyecto['avance'] * 100:.0f}%")

                meta = proyecto["meta"]
                recaudado = proyecto["recaudado"]
                progreso = float(recaudado / meta) if meta > 0 else 0.0

                st.progress(
                    max(0.0, min(progreso, 1.0)),
                    text=f"{cop(recaudado)} de {cop(meta)}",
                )

                faltante = meta - recaudado
                if proyecto["estado"] != "abierto" or faltante <= 0:
                    st.caption(f"Estado: {proyecto['estado']}")
                    continue

                with st.form(
                    f"inv_aporte_{usuario_id}_{proyecto['id']}"
                ):
                    monto = st.number_input(
                        "Monto a invertir (COP)",
                        min_value=0.0,
                        value=0.0,
                        step=50000.0,
                        format="%.2f",
                    )
                    st.caption(f"Disponible para financiar: {cop(faltante)}")
                    enviar = st.form_submit_button(
                        "💰 Invertir — simulación", width="stretch"
                    )

                if enviar:
                    ejecutar_accion(
                        usuario_id,
                        "Inversión simulada guardada en TiDB.",
                        invertir,
                        usuario_id,
                        proyecto["id"],
                        monto,
                    )


def inv_tab_inversiones(usuario_id, datos):
    st.subheader("📊 Mis inversiones")
    st.write("Consulta tus aportes, su rentabilidad estimada y su estado.")

    st.markdown(
        """
    <div class="inv-info-card">
        <div class="inv-card-tag">INFORMACIÓN REGISTRADA</div>
        <div class="inv-info-card-title">📊 Aportes simulados</div>
        <div class="inv-info-card-text">
            Los aportes son simulados. La rentabilidad es una estimación;
            no representa ganancias cobradas ni garantizadas.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button(
        "🔄 Actualizar inversiones",
        key=f"inv_actualizar_inversiones_{usuario_id}",
    ):
        st.rerun()

    inversiones = datos["inversiones"]

    if not inversiones:
        st.info("Aún no tienes inversiones registradas.")
        return

    activas = [i for i in inversiones if i["estado"] != "cancelada"]
    canceladas = [i for i in inversiones if i["estado"] == "cancelada"]
    total = sum(i["monto"] for i in activas)

    met1, met2, met3 = st.columns(3)
    met1.metric("Aportes activos", len(activas))
    met2.metric("Aportes cancelados", len(canceladas))
    met3.metric("Total aportado — sin canceladas", cop(total))

    try:
        rendimientos = total_rendimientos(usuario_id)
        ventas = listar_repartos_inversionista(usuario_id)
    except (ErrorMySQL, ConnectionError):
        rendimientos, ventas = None, []

    st.subheader("💸 Ganancias por ventas")
    if rendimientos is None:
        st.caption("No se pudieron consultar las ganancias.")
    else:
        st.metric("Total ganado por ventas", cop(rendimientos))
        if not ventas:
            st.info(
                "Aún no has recibido ganancias. Aparecerán cuando un comprador "
                "pague un producto de una finca donde invertiste."
            )
        else:
            st.dataframe(
                [
                    {
                        "Fecha": v["fecha"],
                        "Finca": v["finca"],
                        "Producto": v["producto"],
                        "Pago": v["pago_id"],
                        "Ganancia": cop(v["monto"]),
                    }
                    for v in ventas
                ],
                width="stretch",
                hide_index=True,
            )

    st.markdown("---")

    for inversion in inversiones:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### 📊 Inversión #{inversion['id']}")
                st.write(f"**Finca:** {inversion['finca']}")
                st.write(f"**Proyecto:** {inversion['proyecto']}")
                st.write(
                    f"**Rentabilidad estimada:** "
                    f"{inversion['rentabilidad_estimada'] * 100:.1f}%"
                )
                st.caption(f"Fecha: {inversion['creado_en']}")

            with col2:
                st.metric("Valor aportado", cop(inversion["monto"]))

                if inversion["estado"] == "cancelada":
                    st.error("Cancelada")
                else:
                    st.success(str(inversion["estado"]).capitalize())


def inv_tab_wallet(usuario_id, datos):
    st.subheader("👛 Mi wallet digital")
    st.write("Recarga, retira y consulta los movimientos de tu saldo.")
    st.info("Saldo de demostración. Las recargas y retiros son simulados.")
    st.metric("Saldo disponible", cop(datos["saldo"]))

    col_dep, col_ret = st.columns(2)

    with col_dep:
        with st.form(f"inv_recarga_{usuario_id}"):
            dep = st.number_input(
                "Monto a recargar",
                min_value=0.0,
                value=0.0,
                step=50000.0,
                format="%.2f",
            )
            recargar = st.form_submit_button(
                "Recargar saldo simulado", width="stretch"
            )

        if recargar:
            ejecutar_accion(
                usuario_id,
                "Recarga simulada guardada.",
                mover_wallet,
                usuario_id,
                dep,
                "recarga",
            )

    with col_ret:
        with st.form(f"inv_retiro_{usuario_id}"):
            ret = st.number_input(
                "Monto a retirar",
                min_value=0.0,
                value=0.0,
                step=50000.0,
                format="%.2f",
            )
            retirar = st.form_submit_button(
                "Retirar saldo simulado", width="stretch"
            )

        if retirar:
            ejecutar_accion(
                usuario_id,
                "Retiro simulado guardado.",
                mover_wallet,
                usuario_id,
                ret,
                "retiro",
            )

    st.markdown("#### Historial de movimientos")

    filas = [
        {
            "Fecha": movimiento["creado_en"],
            "Tipo": movimiento["tipo"],
            "Monto": cop(movimiento["monto"]),
            "Detalle": movimiento["detalle"],
        }
        for movimiento in datos["movimientos"]
    ]

    if filas:
        st.dataframe(filas, width="stretch", hide_index=True)
    else:
        st.caption("Sin movimientos todavía.")


def ejecutar_modo_inversionista():
    usuario = str(st.session_state.get("usuario", "")).strip()
    if not usuario:
        st.error("Ingresa primero con un usuario.")
        return

    # Datos desde TiDB (igual que antes)
    try:
        usuario_id = iniciar_inversionista(usuario)
        datos = cargar_datos(usuario_id)
    except (ValueError, ErrorMySQL, ConnectionError) as error:
        mostrar_error(error)
        return

    inv_aviso_key = f"inv_aviso_{usuario_id}"
    inv_nombre = datos["perfil"]["nombre"] or usuario

    # ENCABEZADO
    st.markdown(
        f"""
        <div style="
            background:#174B35;
            padding:28px;
            border-radius:18px;
            margin-bottom:20px;
        ">
            <div style="color:#D5E8B8;font-size:15px;">
                AGRITECHGO · INVERSIONISTA
            </div>
            <div style="
                color:#FFFFFF;
                font-size:34px;
                font-weight:750;
                margin:8px 0;
            ">
                AgritechGO
            </div>
            <div style="color:#FFFFFF;font-size:17px;">
                Bienvenido, {escape(str(inv_nombre))}.
                Haz seguimiento a tus inversiones desde un solo lugar.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Tus registros se guardan en TiDB Cloud. "
        "La información se consulta al cargar o actualizar la vista."
    )

    inv_aviso = st.session_state.pop(inv_aviso_key, "")
    if inv_aviso:
        st.success(inv_aviso)

    # MÉTRICAS (con los datos que ya trae TiDB)
    inv_activas = [
        i for i in datos["inversiones"] if i["estado"] != "cancelada"
    ]
    inv_total = sum(i["monto"] for i in inv_activas)
    inv_fincas = {i["finca"] for i in inv_activas}

    inv_col1, inv_col2, inv_col3 = st.columns(3)
    inv_col1.metric("Total aportado", cop(inv_total))
    inv_col2.metric("Fincas financiadas", len(inv_fincas))
    inv_col3.metric("Saldo en wallet", cop(datos["saldo"]))

    st.markdown("---")

    # MENÚ LATERAL DEL INVERSIONISTA
    inv_menu_key = f"inv_menu_{usuario_id}"
    inv_inicio = "📊 Mis inversiones"

    # Se ejecuta antes de volver a dibujar el menú.
    def inv_volver_al_inicio():
        st.session_state[inv_menu_key] = inv_inicio

    inv_logo_path = Path(__file__).resolve().parent.parent / "logo.png"

    inv_boton_inicio_key = f"inv_boton_inicio_{usuario_id}"

    # El logo se usa como imagen de fondo del botón de inicio
    inv_css_logo = ""
    if inv_logo_path.is_file():
        inv_logo_base64 = base64.b64encode(inv_logo_path.read_bytes()).decode("utf-8")
        inv_logo_fondo = f'url("data:image/png;base64,{inv_logo_base64}")'

        inv_css_logo = f"""
            /* LOGO CLICABLE */
            .st-key-{inv_boton_inicio_key} button {{
                background-image: {inv_logo_fondo} !important;
                background-repeat: no-repeat !important;
                background-position: center !important;
                background-size: contain !important;
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
                height: 110px !important;
                min-height: 110px !important;
                color: transparent !important;
                font-size: 0 !important;
                padding: 0 !important;
            }}

            .st-key-{inv_boton_inicio_key} button:hover {{
                background-color: rgba(255,255,255,0.18) !important;
                border-radius: 12px !important;
            }}
        """

    with st.sidebar:

        # ESTILO DEL LOGO Y DEL MENÚ
        st.markdown(
            f"""
            <style>

            {inv_css_logo}

            /* TÍTULO DE NAVEGACIÓN */
            section[data-testid="stSidebar"]
            div[data-testid="stRadio"] > label {{
                font-size: 1.08rem !important;
                font-weight: 750 !important;
            }}

            /* QUITAR CÍRCULOS DE SELECCIÓN */
            section[data-testid="stSidebar"]
            div[data-testid="stRadio"]
            label[data-baseweb="radio"] > div:first-child {{
                display: none !important;
            }}

            /* ESTILO DE CADA OPCIÓN */
            section[data-testid="stSidebar"]
            div[data-testid="stRadio"]
            label[data-baseweb="radio"] {{
                display: flex !important;
                align-items: center !important;
                width: 100% !important;
                box-sizing: border-box !important;
                padding: 0.65rem 0.8rem !important;
                border-radius: 10px !important;
                border-left: 4px solid transparent !important;
                background: transparent !important;
                cursor: pointer !important;
                transition: background 0.2s ease !important;
            }}

            /* TAMAÑO Y COLOR DEL TEXTO */
            section[data-testid="stSidebar"]
            div[data-testid="stRadio"]
            label[data-baseweb="radio"] p {{
                font-size: 1.08rem !important;
                font-weight: 550 !important;
                color: #203D2B !important;
                margin: 0 !important;
            }}

            /* EFECTO AL PASAR EL CURSOR */
            section[data-testid="stSidebar"]
            div[data-testid="stRadio"]
            label[data-baseweb="radio"]:hover {{
                background: #D7E9D0 !important;
            }}

            /* OPCIÓN SELECCIONADA */
            section[data-testid="stSidebar"]
            div[data-testid="stRadio"]
            label[data-baseweb="radio"]:has(input:checked),
            section[data-testid="stSidebar"]
            div[data-testid="stRadio"]
            label[data-baseweb="radio"]:has([aria-checked="true"]) {{
                background: #EAF4E8 !important;
                border-left-color: #2F6B4F !important;
            }}

            /* SEPARACIÓN ENTRE OPCIONES */
            section[data-testid="stSidebar"]
            div[data-testid="stRadio"]
            [role="radiogroup"] {{
                gap: 0.55rem !important;
            }}

            </style>
            """,
            unsafe_allow_html=True,
        )

        # LOGO COMO BOTÓN DE INICIO
        inv_col_izq, inv_col_centro, inv_col_der = st.columns(
            [1, 2, 1],
            gap="small",
        )

        with inv_col_centro:
            st.button(
                "AgritechGO",
                key=inv_boton_inicio_key,
                help="Volver a Mis inversiones",
                on_click=inv_volver_al_inicio,
                width="stretch",
            )

    opcion_menu = st.sidebar.radio(
        "Navegación:",
        [
            "📊 Mis inversiones",
            "🌱 Fincas y proyectos",
            "👛 Wallet",
            "👤 Mi perfil",
        ],
        key=inv_menu_key,
    )

    # PERSONALIZACIÓN VISUAL (misma que el perfil de agricultor)
    st.markdown(
        """
    <style>
        /* FONDO GENERAL DE AGRITECHGO */
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background-color: #EAF4E8 !important;
        }

        /* FONDO DEL MENÚ LATERAL */
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"] {
            background-color: #C5DFBA !important;
        }

        /* TEXTOS DEL MENÚ LATERAL */
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            color: #203D2B !important;
        }

        /* =========================================================
           IDENTIDAD GENERAL
           ========================================================= */

        .inv-ui-note {
            color: #52715D;
            font-size: 0.92rem;
            line-height: 1.5;
            margin: 0.15rem 0 0.9rem 0;
        }

        .inv-card-tag {
            display: inline-block;
            background: #EAF3E8;
            color: #24543B;
            border: 1px solid #B8D5BC;
            border-radius: 999px;
            padding: 4px 11px;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            margin-bottom: 8px;
        }

        /* =========================================================
           CUADROS DE INFORMACIÓN YA REGISTRADA
           BLANCO
           ========================================================= */

        .inv-info-card {
            background: #FFFFFF;
            border: 1px solid #D4E2D6;
            border-left: 5px solid #2F6B4F;
            border-radius: 16px;
            padding: 18px 20px;
            margin: 12px 0;
            box-shadow: 0 4px 14px rgba(23, 75, 53, 0.08);
        }

        .inv-info-card-title {
            color: #173C2A;
            font-size: 1.08rem;
            font-weight: 750;
            margin-bottom: 5px;
        }

        .inv-info-card-text {
            color: #52715D;
            font-size: 0.92rem;
            line-height: 1.5;
        }

        /* =========================================================
           FORMULARIOS
           VERDE CLARO
           ========================================================= */

        div[data-testid="stForm"] {
            background: #F3F9F1 !important;
            border: 1px solid #A9CBAE !important;
            border-left: 6px solid #2F6B4F !important;
            border-radius: 16px !important;
            padding: 1.35rem 1.4rem 1.25rem !important;
            box-shadow: 0 5px 18px rgba(23, 75, 53, 0.09) !important;
        }

        div[data-testid="stForm"] label {
            color: #173C2A !important;
            font-weight: 650 !important;
        }

        div[data-testid="stForm"] input,
        div[data-testid="stForm"] textarea {
            background: #FFFFFF !important;
            border: 1px solid #C7D9CA !important;
            border-radius: 10px !important;
        }

        div[data-testid="stForm"] [data-baseweb="select"] > div {
            background: #FFFFFF !important;
            border-radius: 10px !important;
        }

        div[data-testid="stForm"] [data-testid="stFileUploaderDropzone"] {
            background: #FFFFFF !important;
            border: 1px dashed #9FC3A5 !important;
            border-radius: 12px !important;
        }

        /* =========================================================
           BOTONES
           ========================================================= */

        div[data-testid="stFormSubmitButton"] button {
            background: #174B35 !important;
            color: #FFFFFF !important;
            border: 1px solid #174B35 !important;
            border-radius: 10px !important;
            font-weight: 750 !important;
            min-height: 44px !important;
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            background: #2F6B4F !important;
            border-color: #2F6B4F !important;
        }

        /* =========================================================
           TARJETAS CON BORDER=TRUE
           INFORMACIÓN REGISTRADA
           ========================================================= */

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #FFFFFF !important;
            border: 1px solid #D4E2D6 !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 14px rgba(23, 75, 53, 0.07) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #A9CBAE !important;
            box-shadow: 0 6px 18px rgba(23, 75, 53, 0.11) !important;
        }

        /* TARJETAS DE FINCAS (mismo estilo que los proyectos del agricultor) */
        div[class*="st-key-inv_tarjeta_"] {
            background-color: #FFFFFF !important;
            border: 1px solid #D7E5D8 !important;
            border-left: 6px solid #2E7251 !important;
            border-radius: 16px !important;
            padding: 18px 22px !important;
            margin-bottom: 18px !important;
            box-shadow: 0 3px 12px rgba(30, 70, 45, 0.08) !important;
        }

        div[class*="st-key-inv_tarjeta_"] div[data-testid="stMetric"] {
            background-color: #F3F8F2 !important;
            border: 1px solid #DCE9DC !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
        }

        /* =========================================================
           EXPANDER
           ========================================================= */

        div[data-testid="stExpander"] {
            background: #F8FBF6 !important;
            border: 1px dashed #8FBA98 !important;
            border-radius: 13px !important;
            margin-top: 12px !important;
        }

        div[data-testid="stExpander"] summary {
            color: #24543B !important;
            font-weight: 750 !important;
        }

        /* =========================================================
           MÉTRICAS
           ========================================================= */

        div[data-testid="stMetric"] {
            background: #F8FBF7 !important;
            border: 1px solid #D7E5D9 !important;
            border-radius: 13px !important;
            padding: 10px 14px !important;
        }

        /* =========================================================
           MENSAJES
           ========================================================= */

        div[data-testid="stAlert"] {
            border-radius: 12px !important;
        }

        /* =========================================================
           INPUTS FUERA DE FORMULARIO
           ========================================================= */

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            border-radius: 10px !important;
        }

        /* =========================================================
           RESPONSIVE
           ========================================================= */

        @media (max-width: 768px) {

            div[data-testid="stForm"] {
                padding: 1rem !important;
                border-left-width: 4px !important;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 13px !important;
            }
        }

    </style>
    """,
        unsafe_allow_html=True,
    )

    # AYUDA SEGÚN LA SECCIÓN SELECCIONADA
    inv_ayudas_menu = {
        "📊 Mis inversiones": "Consulta tus aportes, su rentabilidad estimada y su estado.",
        "🌱 Fincas y proyectos": "Sigue fincas y revisa los proyectos que puedes financiar.",
        "👛 Wallet": "Recarga, retira y revisa los movimientos de tu saldo.",
        "👤 Mi perfil": "Actualiza tu foto y la descripción de tu perfil.",
    }

    st.sidebar.markdown("---")
    st.sidebar.info(inv_ayudas_menu[opcion_menu])

    # SECCIÓN ELEGIDA EN EL MENÚ
    if opcion_menu == "📊 Mis inversiones":
        inv_tab_inversiones(usuario_id, datos)

    elif opcion_menu == "🌱 Fincas y proyectos":
        inv_tab_fincas(usuario_id, datos)

    elif opcion_menu == "👛 Wallet":
        inv_tab_wallet(usuario_id, datos)

    elif opcion_menu == "👤 Mi perfil":
        inv_tab_perfil(usuario_id, datos)


print("POR EL EMPERADOR!!!")