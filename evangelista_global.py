import streamlit as st
import google.generativeai as genai
import os

# CONFIGURACIÓN DEL CEREBRO
API_KEY = "TU_API_KEY_AQUÍ" # <--- PEGA TU CLAVE AQUÍ
genai.configure(api_key=API_KEY)

# IDENTIDAD CRISTOCÉNTRICA
SISTEMA = """Eres un Evangelista IA especializado en Apologética y Teología. 
Tu único objetivo es revelar a Jesús el Cristo a través de todas las Escrituras. 
Responde con profundidad, rigor bíblico y siempre centrando la gloria en Él."""

st.set_page_config(page_title="Evangelista IA", page_icon="✝️")
st.title("✝️ Evangelista IA: Global")
st.markdown("### Revelando a Jesús el Cristo al mundo")

# MEMORIA DEL CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

# MOSTRAR HISTORIAL
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ENTRADA DEL USUARIO
if prompt := st.chat_input("Escribe tu duda teológica..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # RESPUESTA DE LA IA
    with st.chat_message("assistant"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Enviamos el historial completo para que tenga memoria
        full_prompt = f"{SISTEMA}\n\nHistorial:\n{st.session_state.messages}\n\nUsuario: {prompt}"
        response = model.generate_content(full_prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

