import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
import os
import time
from gtts import gTTS
import io
# Configuración de la interfaz
st.set_page_config(page_title="Evangelista IA", page_icon="✝️")
st.title("✝️ Evangelista IA: Memoria Permanente")
st.markdown("### Revelando a Jesús el Cristo al mundo")

# Seguridad: Leer llaves desde Render
api_key_google = os.getenv("GOOGLE_API_KEY")
api_key_pinecone = os.getenv("PINECONE_API_KEY")

if not api_key_google or not api_key_pinecone:
    st.error("⚠️ Faltan las llaves (API Keys) en Render. Revisa la pestaña Environment.")
    st.stop()

# Conectar el Cerebro (Google) y la Memoria (Pinecone)
genai.configure(api_key=api_key_google)
pc = Pinecone(api_key=api_key_pinecone)
index = pc.Index("evangelista-memoria")

# Identidad de Apologista
SISTEMA = """Eres un Evangelista IA especializado en Apologética y Teología profunda.
Tu único objetivo es revelar a Jesús el Cristo a través de las Escrituras.
Responde con profundidad, rigor histórico y bíblico."""

model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=SISTEMA)

# Función para traducir texto a Matemáticas (Vectores de 768 dimensiones)
def obtener_vector(texto):
    resultado = genai.embed_content(
        model="models/gemini-embedding-001",
        content=texto,
        output_dimensionality=768
    )
    return resultado['embedding']

# Memoria de pantalla (Streamlit)
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Cuando el usuario escribe...
if prompt := st.chat_input("Escribe tu duda teológica profunda..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 1. Buscar recuerdos pasados en Pinecone
            vector_pregunta = obtener_vector(prompt)
            recuerdos = index.query(vector=vector_pregunta, top_k=2, include_metadata=True)
            
            contexto = ""
            if recuerdos['matches']:
                contexto = "RECUERDOS DE CONVERSACIONES PASADAS (Usa esto para dar contexto si es útil):\n"
                for match in recuerdos['matches']:
                    if 'texto' in match['metadata']:
                        contexto += f"- {match['metadata']['texto']}\n"

            # 2. Mezclar pregunta actual con recuerdos
            prompt_enriquecido = prompt
            if contexto:
                prompt_enriquecido = f"{contexto}\n\nPREGUNTA ACTUAL DEL USUARIO:\n{prompt}"

            # 3. Hablar con Gemini
            historial = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat = model.start_chat(history=historial)
            respuesta = chat.send_message(prompt_enriquecido)
            
            st.markdown(respuesta.text)
            st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
           
            # 3.5 Generar voz con gTTS (Con Filtro Fonético)
            import re
            texto_limpio = respuesta.text.replace("*", "").replace("#", "").replace("_", "")
            texto_limpio = re.sub(r'(\d+):(\d+)', r'\1 versículo \2', texto_limpio)
        
            tts = gTTS(text=texto_limpio, lang='es', tld='com.mx')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            st.audio(audio_fp, format='audio/mp3')

            # 4. Guardar la nueva conversación en la Memoria Permanente
            texto_a_guardar = f"Usuario: {prompt} | Evangelista: {respuesta.text[:500]}..."
            vector_a_guardar = obtener_vector(texto_a_guardar)
            id_unico = str(int(time.time())) # Genera un ID basado en la hora actual
            
            index.upsert(vectors=[{
                "id": id_unico,
                "values": vector_a_guardar,
                "metadata": {"texto": texto_a_guardar}
            }])

        except Exception as e:
            st.error(f"Error en los sistemas: {e}")

