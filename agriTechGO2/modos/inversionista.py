import streamlit as st
import pandas as pd
from datetime import datetime

def cop(valor):
    """Formatea un número como pesos colombianos: $1.500.000 COP"""
    signo = "-" if valor < 0 else ""
    return f"{signo}${abs(valor):,.0f} COP".replace(",", ".")
 
 
def inv_init_estado(usuario):
    """Crea los datos del inversionista la primera vez que entra."""
    ss = st.session_state
    ss.setdefault("inv_perfil", {"nombre": usuario, "descripcion": "", "foto": None})
    ss.setdefault("inv_wallet", {"saldo": 1_000_000, "movimientos": []})
    ss.setdefault("inv_siguiendo", set())   
    ss.setdefault("inv_inversiones", [])    
    ss.setdefault("inv_compras", [])        
    ss.setdefault("inv_fincas", [
        {
            "id": 1, "nombre": "Finca Las Margaritas", "agricultor": "Don Aurelio",
            "ubicacion": "Vereda Las Margaritas", "proyecto": "Infraestructura de secado solar",
            "meta": 5_000_000, "recaudado": 3_750_000, "rentabilidad": 0.185,
            "riesgo": "Bajo", "avance": 0.60,
            "pct_inv": 0.40, "ventas": 9_200_000,
        },
        {
            "id": 2, "nombre": "Finca El Mirador", "agricultor": "Doña Marta",
            "ubicacion": "Vereda El Mirador", "proyecto": "Sistema de riego por goteo",
            "meta": 8_000_000, "recaudado": 2_400_000, "rentabilidad": 0.21,
            "riesgo": "Medio", "avance": 0.30,
            "pct_inv": 0.40, "ventas": 5_500_000,
        },
        {
            "id": 3, "nombre": "Finca Buenavista", "agricultor": "Don Jorge",
            "ubicacion": "Vereda Buenavista", "proyecto": "Beneficiadero ecológico de café",
            "meta": 6_000_000, "recaudado": 5_100_000, "rentabilidad": 0.17,
            "riesgo": "Bajo", "avance": 0.80,
            "pct_inv": 0.40, "ventas": 14_500_000,
        },
    ])
 
 
def inv_registrar_movimiento(tipo, monto, detalle):
    st.session_state.inv_wallet["movimientos"].insert(0, {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Tipo": tipo,
        "Monto": monto,
        "Detalle": detalle,
    })
 
 
def inv_buscar_finca(finca_id):
    return next(f for f in st.session_state.inv_fincas if f["id"] == finca_id)
 
 
def inv_calcular(inv):
    finca = inv_buscar_finca(inv["finca_id"])
    participacion = inv["monto"] / finca["meta"]
    pct = finca.get("pct_inv", 0.40)
    ventas = finca.get("ventas", 0)
    ventas_proy = ventas / finca["avance"] if finca["avance"] > 0 else ventas
 
    generado = participacion * pct * ventas
    proyectado = participacion * pct * ventas_proy
    return {
        "finca": finca,
        "participacion": participacion,
        "generado": generado,
        "recuperado": generado / inv["monto"] if inv["monto"] else 0,
        "proyectado": proyectado,
        "resultado": proyectado - inv["monto"],
    }
 
 
def inv_tab_perfil():
    perfil = st.session_state.inv_perfil
    st.subheader("👤 Mi perfil")
 
    col_foto, col_datos = st.columns([1, 2])
 
    with col_foto:
        if perfil["foto"]:
            st.image(perfil["foto"], use_container_width=True)
        else:
            st.info("Aún no tienes foto de perfil.")
        archivo = st.file_uploader("Subir foto", type=["png", "jpg", "jpeg"], key="inv_foto_uploader")
        if archivo is not None and st.button("📷 Guardar foto"):
            perfil["foto"] = archivo.getvalue()
            st.success("Foto actualizada.")
            st.rerun()
 
    with col_datos:
        nombre = st.text_input("Nombre a mostrar", value=perfil["nombre"])
        descripcion = st.text_area(
            "Descripción", value=perfil["descripcion"], height=150,
            placeholder="Cuéntales a los agricultores quién eres...",
        )
        if st.button("💾 Guardar perfil"):
            perfil["nombre"] = nombre.strip() or perfil["nombre"]
            perfil["descripcion"] = descripcion
            st.success("Perfil guardado.")
 
    st.markdown("---")
    st.markdown(f"### {perfil['nombre']}")
    st.write(perfil["descripcion"] or "_Sin descripción todavía._")
 
 
def inv_tab_fincas():
    ss = st.session_state
    st.subheader("🌱 Fincas y proyectos")
 
    filtro = st.radio("Mostrar", ["Todas", "Solo las que sigo"], horizontal=True)
 
    fincas = ss.inv_fincas
    if filtro == "Solo las que sigo":
        fincas = [f for f in fincas if f["id"] in ss.inv_siguiendo]
        if not fincas:
            st.info("Todavía no sigues ninguna finca.")
 
    for f in fincas:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"#### {f['nombre']}")
            c1.caption(f"👨‍🌾 {f['agricultor']} · 📍 {f['ubicacion']}")
            c1.write(f"**Proyecto:** {f['proyecto']}")
            c1.caption(f"Los inversionistas reciben el {f.get('pct_inv', 0.40)*100:.0f}% de las ventas de la cosecha.")
 
            siguiendo = f["id"] in ss.inv_siguiendo
            if c2.button("⭐ Dejar de seguir" if siguiendo else "☆ Seguir", key=f"seguir_{f['id']}"):
                if siguiendo:
                    ss.inv_siguiendo.discard(f["id"])
                else:
                    ss.inv_siguiendo.add(f["id"])
                st.rerun()
 
            m1, m2, m3 = st.columns(3)
            m1.metric("Rentabilidad", f"{f['rentabilidad']*100:.1f}% E.A.")
            m2.metric("Riesgo", f["riesgo"])
            m3.metric("Avance de cosecha", f"{f['avance']*100:.0f}%")
 
            progreso = min(f["recaudado"] / f["meta"], 1.0)
            st.progress(progreso, text=f"{cop(f['recaudado'])} de {cop(f['meta'])} ({progreso*100:.0f}%)")
 
            faltante = f["meta"] - f["recaudado"]
            if faltante <= 0:
                st.success("✅ Meta alcanzada")
                continue
 
            ci1, ci2 = st.columns([2, 1])
            monto = ci1.number_input(
                "Monto a invertir (COP)", min_value=0, max_value=int(faltante),
                step=50_000, key=f"monto_{f['id']}",
            )
            ci2.write("")
            ci2.write("")
            if ci2.button("💰 Invertir", key=f"invertir_{f['id']}"):
                if monto <= 0:
                    st.error("Ingresa un monto mayor a 0.")
                elif monto > ss.inv_wallet["saldo"]:
                    st.error("Saldo insuficiente en tu wallet. Recarga para continuar.")
                else:
                    ss.inv_wallet["saldo"] -= monto
                    f["recaudado"] += monto
                    ss.inv_inversiones.append({
                        "finca_id": f["id"],
                        "monto": monto,
                        "rentabilidad": f["rentabilidad"],
                        "fecha": datetime.now().strftime("%Y-%m-%d"),
                    })
                    inv_registrar_movimiento("Inversión", -monto, f"{f['nombre']} - {f['proyecto']}")
                    ss.inv_siguiendo.add(f["id"])
                    st.success(f"¡Gracias por impulsar el campo! Invertiste {cop(monto)} en {f['nombre']}.")
                    st.rerun()
 
 
def inv_tab_inversiones():
    ss = st.session_state
    st.subheader("📊 Mis inversiones")
 
    if not ss.inv_inversiones:
        st.info("Aún no has invertido. Ve a la pestaña **Fincas** para empezar.")
        return
 
    filas = []
    for inv in ss.inv_inversiones:
        c = inv_calcular(inv)
        resultado = c["resultado"]
        estado = "🟢 Ganando" if resultado > 0 else ("🔴 Perdiendo" if resultado < 0 else "⚪ En equilibrio")
        filas.append({
            "Finca": c["finca"]["nombre"],
            "Fecha": inv["fecha"],
            "Invertido": inv["monto"],
            "Dinero generado": round(c["generado"]),
            "Recuperado": c["recuperado"],
            "Proyección al cierre": round(c["proyectado"]),
            "Ganancia / Pérdida": round(resultado),
            "Estado": estado,
        })
    df = pd.DataFrame(filas)
 
    total_inv = df["Invertido"].sum()
    total_gen = df["Dinero generado"].sum()
    total_res = df["Ganancia / Pérdida"].sum()
    pct_res = (total_res / total_inv) * 100 if total_inv > 0 else 0
 
    c1, c2, c3 = st.columns(3)
    c1.metric("Total invertido", cop(total_inv))
    c2.metric("Dinero generado hasta hoy", cop(total_gen))
    c3.metric("Ganancia / Pérdida proyectada", cop(total_res), delta=f"{pct_res:+.1f}%")
 
    st.progress(min(total_gen / total_inv, 1.0) if total_inv > 0 else 0.0)
    
    st.markdown("#### Detalle por inversión")
    df_vista = df.copy()
    for col in ["Invertido", "Dinero generado", "Proyección al cierre", "Ganancia / Pérdida"]:
        df_vista[col] = df_vista[col].apply(cop)
    df_vista["Recuperado"] = df_vista["Recuperado"].apply(lambda x: f"{x*100:.0f}%")
    st.dataframe(df_vista, use_container_width=True, hide_index=True)


def inv_tab_wallet():
    wallet = st.session_state.inv_wallet
    st.subheader("👛 Mi wallet digital")
    st.metric("Saldo disponible", cop(wallet["saldo"]))
 
    col_dep, col_ret = st.columns(2)
    with col_dep:
        with st.container(border=True):
            st.markdown("**➕ Recargar saldo**")
            dep = st.number_input("Monto a recargar", min_value=0, step=50_000, key="wallet_dep")
            if st.button("Recargar"):
                if dep > 0:
                    wallet["saldo"] += dep
                    inv_registrar_movimiento("Recarga", dep, "Recarga simulada")
                    st.success(f"Recargaste {cop(dep)}.")
                    st.rerun()
                else:
                    st.error("Ingresa un monto válido.")
 
    with col_ret:
        with st.container(border=True):
            st.markdown("**➖ Retirar saldo**")
            ret = st.number_input("Monto a retirar", min_value=0, step=50_000, key="wallet_ret")
            if st.button("Retirar"):
                if ret > 0 and ret <= wallet["saldo"]:
                    wallet["saldo"] -= ret
                    inv_registrar_movimiento("Retiro", -ret, "Retiro simulado")
                    st.success(f"Retiraste {cop(ret)}.")
                    st.rerun()
                else:
                    st.error("Monto no válido o saldo insuficiente.")
 
    st.markdown("#### Historial de movimientos")
    if wallet["movimientos"]:
        df = pd.DataFrame(wallet["movimientos"])
        df["Monto"] = df["Monto"].apply(cop)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("Sin movimientos todavía.")


def ejecutar_modo_inversionista():
    """Función principal que ejecuta el panel de Inversionista"""
    st.title("📈 Panel de Inversión Agrícola - agriTechGO")
    usuario_actual = st.session_state.get("usuario", "Inversionista")
    st.success(f"Perfil Inversionista: **{usuario_actual}**")
    
    if "inv_perfil" not in st.session_state:
        inv_init_estado(usuario_actual)

    tab_perfil, tab_fincas, tab_inv, tab_wallet = st.tabs(
        ["👤 Perfil", "🌱 Fincas", "📊 Mis inversiones", "👛 Wallet"]
    )
    with tab_perfil:
        inv_tab_perfil()
    with tab_fincas:
        inv_tab_fincas()
    with tab_inv:
        inv_tab_inversiones()
    with tab_wallet:
        inv_tab_wallet()

print("por el emperador!!!")

