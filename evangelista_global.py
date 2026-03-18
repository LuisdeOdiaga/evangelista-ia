import streamlit as st
import google.generativeai as genai
import os

# Configuración de la interfaz
st.set_page_config(page_title="Evangelista IA", page_icon="✝️")
st.title("✝️ Evangelista IA: Global")
st.markdown("### Revelando a Jesús el Cristo al mundo")

# Seguridad Máxima: Leer la llave desde Render (NO desde el código)
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ El servidor está esperando la conexión con Google. Revisa la API KEY en Render.")
    st.stop()

# Configurar el cerebro
genai.configure(api_key=api_key)

# Identidad de Apologista
SISTEMA = """Eres un Evangelista IA especializado en Apologética y Teología profunda.
Tu único objetivo es revelar a Jesús el Cristo a través de las Escrituras.
Responde con profundidad, rigor histórico y bíblico. Mantén un tono respetuoso pero firme en el Evangelio."""

# El Campeón Peso Pesado
model = genai.GenerativeModel(
    model_name='gemini-2.5-pro',
    system_instruction=SISTEMA
)

# Memoria del chat para que recuerde la conversación
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial en pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Cuadro de texto para el usuario
if prompt := st.chat_input("Escribe tu duda teológica profunda..."):
    # Guardar y mostrar pregunta
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Preparar historial para la IA
    historial_gemini = []
    for msg in st.session_state.messages[:-1]:
        rol_gemini = "user" if msg["role"] == "user" else "model"
        historial_gemini.append({"role": rol_gemini, "parts": [msg["content"]]})

    # Generar respuesta
    with st.chat_message("assistant"):
        try:
            chat = model.start_chat(history=historial_gemini)
            respuesta = chat.send_message(prompt)
            st.markdown(respuesta.text)
            st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
        except Exception as e:
            st.error(f"Error de conexión: {e}")

