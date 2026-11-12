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


def cop(valor):

    signo = "-" if valor < 0 else ""
    return f"{signo}${abs(valor):,.0f} COP".replace(",", ".")


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
    st.subheader("👤 Mi perfil")

    col_foto, col_datos = st.columns([1, 2])

    with col_foto:
        if perfil["foto"]:
            st.image(perfil["foto"], use_container_width=True)
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
            guardar = st.form_submit_button("💾 Guardar perfil")

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

    filtro = st.radio(
        "Mostrar",
        ["Todas", "Solo las que sigo"],
        horizontal=True,
        key=f"inv_filtro_{usuario_id}",
    )

    fincas = datos["fincas"]
    if filtro == "Solo las que sigo":
        fincas = [
            finca for finca in fincas
            if finca["id"] in datos["siguiendo"]
        ]

    if not fincas:
        st.info("No hay fincas para mostrar con este filtro.")
        return

    for finca in fincas:
        with st.container(border=True):
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
                    enviar = st.form_submit_button("💰 Invertir — simulación")

                if enviar:
                    ejecutar_accion(
                        usuario_id,
                        "Inversión simulada guardada en TiDB.",
                        invertir,
                        usuario_id,
                        proyecto["id"],
                        monto,
                    )


def inv_tab_inversiones(datos):
    st.subheader("📊 Mis inversiones")
    inversiones = datos["inversiones"]

    if not inversiones:
        st.info("Aún no tienes inversiones registradas.")
        return

    total = sum(
        inversion["monto"]
        for inversion in inversiones
        if inversion["estado"] != "cancelada"
    )
    st.metric("Total aportado — sin canceladas", cop(total))
    st.caption(
        "Los aportes son simulados. La rentabilidad es una estimación; "
        "no representa ganancias cobradas ni garantizadas."
    )

    filas = []
    for inversion in inversiones:
        filas.append({
            "ID": inversion["id"],
            "Finca": inversion["finca"],
            "Proyecto": inversion["proyecto"],
            "Fecha": inversion["creado_en"],
            "Invertido": cop(inversion["monto"]),
            "Rentabilidad estimada": (
                f"{inversion['rentabilidad_estimada'] * 100:.1f}%"
            ),
            "Estado": inversion["estado"],
        })

    st.dataframe(filas, use_container_width=True, hide_index=True)


def inv_tab_wallet(usuario_id, datos):
    st.subheader("👛 Mi wallet digital")
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
            recargar = st.form_submit_button("Recargar saldo simulado")

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
            retirar = st.form_submit_button("Retirar saldo simulado")

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
        st.dataframe(filas, use_container_width=True, hide_index=True)
    else:
        st.caption("Sin movimientos todavía.")


def ejecutar_modo_inversionista():
    usuario = str(st.session_state.get("usuario", "")).strip()
    if not usuario:
        st.error("Ingresa primero con un usuario.")
        return

    st.title("📈 Panel de Inversión Agrícola - agriTechGO")

    try:
        usuario_id = iniciar_inversionista(usuario)
        datos = cargar_datos(usuario_id)
    except (ValueError, ErrorMySQL, ConnectionError) as error:
        mostrar_error(error)
        return

    st.success(f"Perfil Inversionista: {datos['perfil']['nombre']}")
    st.caption("Información guardada en TiDB Cloud.")

    aviso = st.session_state.pop(f"inv_aviso_{usuario_id}", "")
    if aviso:
        st.success(aviso)

    if st.button("🔄 Actualizar información"):
        st.rerun()

    tab_perfil, tab_fincas, tab_inv, tab_wallet = st.tabs(
        ["👤 Perfil", "🌱 Fincas", "📊 Mis inversiones", "👛 Wallet"]
    )

    with tab_perfil:
        inv_tab_perfil(usuario_id, datos)

    with tab_fincas:
        inv_tab_fincas(usuario_id, datos)

    with tab_inv:
        inv_tab_inversiones(datos)

    with tab_wallet:

        inv_tab_wallet(usuario_id, datos)

        inv_tab_wallet()

print("por el emperador!!!")

