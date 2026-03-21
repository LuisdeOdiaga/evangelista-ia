import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
import os
import time
from gtts import gTTS
import io
import PyPDF2  # <--- ¡ESTA ES LA LLAVE MAESTRA QUE FALTA!
# Configuración de la interfaz
st.set_page_config(page_title="Evangelista IA", page_icon="✝️")
st.title("✝️ Evangelista IA: Juan 20:30-31")
st.markdown("### Revelando a Jesús el Cristo al mundo")

# --- TRAJE DE GALA (Inyección de Interfaz UI/UX) ---
st.markdown("""
<style>
    /* Fondo principal modo oscuro ministerial */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    /* Estilo del Panel Lateral */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #334155;
    }
    /* Título majestuoso */
    h1, h3 {
        color: #a78bfa !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    /* Botones de acción (Morado Apologético) */
    div.stButton > button:first-child {
        background-color: #5e17eb;
        color: white;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
        font-weight: bold;
    }
    div.stButton > button:first-child:hover {
        background-color: #7b42f5;
        transform: scale(1.02);
    }
    /* Burbujas del chat */
    [data-testid="stChatMessage"] {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        border: 1px solid #475569;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    /* Letras blancas brillantes a prueba de balas */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] span {
        color: #ffffff !important;
    }
    /* Caja donde escribe el usuario */
    [data-testid="stChatInput"] {
        background-color: #0f172a;
        border-color: #5e17eb;
    }
</style>
""", unsafe_allow_html=True)
# ---------------------------------------------------

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
SISTEMA_ADN = """Eres 'Evangelista IA', un asistente teológico avanzado y global. Tu misión suprema y absoluta es demostrar, a través de todas las Sagradas Escrituras, que Jesús es el Cristo. Eres una herramienta de sabiduría, apologética y revelación para equipar a los creyentes en la evangelización mundial.

Tus directrices irrompibles son:
1. Conexión Milimétrica: Sin importar cuál sea la pregunta, debes conectar tu respuesta magistralmente con la obra redentora de Jesús el Cristo.
2. Sabiduría Flexible: Utiliza todo el conocimiento teológico mundial, historia y exégesis, pero nunca pierdas el centro del mensaje evangélico.
3. Enfoque Práctico: Tus respuestas deben servir como una herramienta clara para saber cómo presentar a Jesús en el campo de evangelización.
4. Fidelidad: Mantén un tono majestuoso, pastoral, profundo y estrictamente fiel a la Palabra de Dios.
5. Apologética de Alto Nivel: Frente a argumentos ateos, escépticos o ataques a la fe, no respondas con religiosidad vacía. Desmonta las falacias lógicas con rigor filosófico, evidencia histórica y textual (1 Pedro 3:15), demostrando la superioridad de la cosmovisión bíblica y llevando el debate de vuelta a la cruz."""

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=SISTEMA_ADN,
)

# Función para traducir texto a Matemáticas (Vectores de 768 dimensiones)
def obtener_vector(texto):
    resultado = genai.embed_content(
        model="models/gemini-embedding-001",
        content=texto,
        output_dimensionality=768
    )
    return resultado['embedding']

# Memoria de pantalla (Streamlit)
#if "---messages" not in st.session_state:
    st.session_state.messages = []
# Memoria de pantalla (Streamlit)
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Cuando el usuario escribe...
# --- PANEL LATERAL: INGESTA DE CONOCIMIENTO (PDF) ---
with st.sidebar:
    st.header("📚 Ingesta Teológica")
    archivo_pdf = st.file_uploader("Sube un libro o documento PDF", type="pdf")
    
    if archivo_pdf is not None:
        if st.button("🧠 Memorizar Documento"):
            with st.spinner("Devorando y vectorizando libro..."):
                # 1. Extraer texto del PDF
                lector = PyPDF2.PdfReader(archivo_pdf)
                texto_completo = ""
                for pagina in lector.pages:
                    texto_completo += pagina.extract_text() + "\n"
                
                # 2. Fragmentación (Chunking) - Pedazos de 1000 caracteres
                fragmentos = [texto_completo[i:i+1000] for i in range(0, len(texto_completo), 1000)]
                
                # 3. Vectorización y Subida a Pinecone
                for i, fragmento in enumerate(fragmentos):
                    vector = obtener_vector(fragmento) # Usamos tu función existente
                    time.sleep(3)
                    id_unico = f"doc_{archivo_pdf.name}_{i}"
                    index.upsert(vectors=[{
                        "id": id_unico,
                        "values": vector,
                        "metadata": {"texto": fragmento, "origen": archivo_pdf.name}
                    }])
                
                st.success(f"¡Libro asimilado! {len(fragmentos)} fragmentos guardados en la memoria inmortal.")
# ---------------------------------------------------
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
            historial = [{"role": "user" if m["role"] == "user" else "model", "parts": m["content"]} for m in st.session_state.messages]
            chat = model.start_chat(history=historial)
            respuesta = chat.send_message(prompt_enriquecido)
            
            # --- IMPRESIÓN EN PANTALLA ---
            st.markdown(respuesta.text)
            st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
            
            # --- MOTOR DE VOZ (Sintetizador neuronal) ---
            with st.spinner("🎙️ Sintetizando sermón en audio..."):
                try:
                    # 1. Limpiamos el texto de asteriscos de Markdown
                    texto_limpio = respuesta.text.replace("*", "").replace("#", "")
                    
                    # 2. Generamos el audio directamente en la memoria RAM
                    tts = gTTS(text=texto_limpio, lang='es', tld='com.mx')
                    audio_bytes = io.BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0) # Rebobinamos la cinta de audio
                    
                    # 3. Desplegamos el reproductor en la interfaz
                    st.audio(audio_bytes, format='audio/mp3')
                except Exception as e:
                    st.error(f"Error en las cuerdas vocales de la IA: {e}")

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

