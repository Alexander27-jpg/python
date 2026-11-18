import os
import streamlit as st
import google.generativeai as genai

# Configura tu clave de API de Gemini (o usa el respaldo local)
API_KEY_GEMINI = st.secrets.get("GEMINI_API_KEY", "TU_API_KEY_AQUI")

if API_KEY_GEMINI != "TU_API_KEY_AQUI":
    genai.configure(api_key=API_KEY_GEMINI)


def obtener_respuesta_ia(pregunta):
    """Usa Gemini para responder con inteligencia artificial sobre AgriTechGO"""
    prompt_sistema = """
    Eres AgriBot, el asistente virtual oficial de AgriTechGO, una plataforma web y móvil desarrollada en Colombia (Cúcuta) 
    por estudiantes de ingeniería de sistemas de la Universidad Simón Bolívar. 
    El objetivo de AgriTechGO es eliminar a los intermediarios conectando directamente a los caficultores y agricultores 
    con compradores directos e inversionistas agro. 
    Tienes tres perfiles principales: Agricultor/Caficultor, Comprador Directo e Inversionista Agro.
    Responde de forma amable, profesional, con un toque caribeño/colombiano sutil, y orientada a la agricultura.
    """

    try:
        if API_KEY_GEMINI != "TU_API_KEY_AQUI":
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=prompt_sistema
            )
            response = model.generate_content(pregunta)
            return response.text
    except Exception:
        pass

    # Respaldo local si no hay internet o clave
    p = pregunta.lower().strip()
    if any(w in p for w in ["hola", "buenas", "hey"]):
        return "¡Hola, parce! 👋 Soy AgriBot. ¿En qué te puedo colaborar con el proyecto de AgriTechGO?"
    elif any(w in p for w in ["precio", "cafe", "café", "cacao"]):
        return "📊 Los precios de referencia actuales son: Café Pergamino ($2.213.250 COP la carga) y Cacao Seco ($28.400 COP/kg)."
    elif any(w in p for w in ["rol", "perfil", "agricultor", "comprador", "inversionista"]):
        return "🚜 Manejamos 3 perfiles: Agricultores (publican cosechas), Compradores Directos e Inversionistas Agro."
    else:
        return f"🤖 Entiendo tu pregunta sobre '{pregunta}'. AgriTechGO es la plataforma líder para conectar el campo colombiano sin intermediarios."


def renderizar_chatbot():
    """Renderiza una burbuja flotante redonda verde grande en la esquina inferior derecha"""
    if "mensajes_bot" not in st.session_state:
        st.session_state.mensajes_bot = [
            {
                "role": "assistant",
                "content": "¡Hola! 🌱 Soy AgriBot. Pregúntame lo que quieras sobre AgriTechGO o los precios del agro.",
            }
        ]

    # Contenedor flotante fijado estrictamente abajo a la derecha
    st.markdown(
        """
        <style>
            .floating-chatbot-container {
                position: fixed !important;
                bottom: 30px !important;
                right: 30px !important;
                z-index: 999999 !important;
            }
            
            /* Convierte el botón en un círculo verde GRANDE y llamativo */
            .floating-chatbot-container [data-testid="stPopover"] > button {
                background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%) !important;
                color: white !important;
                width: 72px !important;
                min-width: 72px !important;
                height: 72px !important;
                min-height: 72px !important;
                border-radius: 50% !important;
                padding: 0px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-size: 32px !important;
                border: 3px solid #74c69d !important;
                box-shadow: 0 10px 30px rgba(27, 67, 50, 0.8) !important;
                transition: transform 0.2s ease, box-shadow 0.2s ease !important;
            }
            
            .floating-chatbot-container [data-testid="stPopover"] > button:hover {
                background: linear-gradient(135deg, #40916c 0%, #2d6a4f 100%) !important;
                transform: scale(1.12);
                box-shadow: 0 14px 35px rgba(116, 198, 157, 0.9) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Renderizamos el componente dentro de la capa flotante
    with st.container():
        st.markdown('<div class="floating-chatbot-container">', unsafe_allow_html=True)
        
        with st.popover("💬"):
            st.markdown("#### 🌱 AgriBot - Asistente IA")
            contenedor_chat = st.container(height=300)

            with contenedor_chat:
                for msg in st.session_state.mensajes_bot:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            prompt = st.chat_input("Escribe tu pregunta...", key="input_agribot")
            if prompt:
                st.session_state.mensajes_bot.append({"role": "user", "content": prompt})
                respuesta = obtener_respuesta_ia(prompt)
                st.session_state.mensajes_bot.append({"role": "assistant", "content": respuesta})
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)