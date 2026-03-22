import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
import os
import time
import io
import base64
import PyPDF2  # <--- ¡ESTA ES LA LLAVE MAESTRA QUE FALTA!
# Configuración de la interfaz
st.set_page_config(page_title="Evangelista IA", page_icon="✝️")
st.title("✝️ Evangelista IA: Juan 20:30-31")
st.markdown("### Revelando a Jesús el Cristo al mundo")

# --- MUTACIÓN A APP NATIVA (PWA Nivel Dios) ---
manifest_json = """
{
  "name": "Evangelista IA Apologética",
  "short_name": "Evangelista",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#0b0f19",
  "theme_color": "#5e17eb",
  "icons": [
    {
      "src": "https://cdn-icons-png.flaticon.com/512/3004/3004458.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
"""
b64_manifest = base64.b64encode(manifest_json.encode('utf-8')).decode('utf-8')
st.markdown(f'<link rel="manifest" href="data:application/manifest+json;base64,{b64_manifest}">', unsafe_allow_html=True)
# ----------------------------------------------

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

# --- Evangelización Mundial (Control de Acceso de Dos Niveles) ---
if not st.session_state.autenticado:
     st.markdown("### 🔐 Acceso al Búnker Teológico")
     usuario = st.text_input("👤 Usuario")
     clave = st.text_input("🔑 Contraseña", type="password")
if st.button("Entrar"):
     admin_u = os.getenv("ADMIN_USER", "admin")
     admin_p = os.getenv("ADMIN_PASS", "admin")
     guest_u = os.getenv("GUEST_USER", "invitado")
     guest_p = os.getenv("GUEST_PASS", "1234")
if usuario == admin_u and clave == admin_p:
     st.session_state.autenticado = True
     st.session_state.rol = "admin"
     st.rerun()
elif usuario == guest_u and clave == guest_p:
     st.session_state.autenticado = True
     st.session_state.rol = "invitado"
     st.rerun()
else:
     st.error("🚨 Credenciales incorrectas.")
     st.stop()
# -------------------------------------------------------

# Seguridad: Leer llaves desde Render
api_key_google = os.getenv("GOOGLE_API_KEY")
api_key_pinecone = os.getenv("PINECONE_API_KEY")

if not api_key_google or not api_key_pinecone:
    st.error("⚠️ Faltan las llaves (API Keys) en Render. Revisa Google o Pinecone.")
    st.stop()

# Conectar Motores
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
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
    st.markdown(message["content"])

## --- ---MOTOR VISUAL ---
# --- PANEL LATERAL EXCLUSIVO PARA EL ARQUITECTO ---
if st.session_state.rol == "admin":
    with st.sidebar:
    st.header("📚 Ingesta Teológica")
    archivo_pdf = st.file_uploader("Sube un libro o documento doctrinal (PDF)", type=["pdf"])
        
if archivo_pdf is not None:
if st.button("🧠 Memorizar Documento"):
    with st.spinner("Devorando y vectorizando libro..."):
# 1. Extraer texto del PDF
    lector = PyPDF2.PdfReader(archivo_pdf)
    texto_completo = ""
    for pagina in lector.pages:
    texto_completo += pagina.extract_text()
                    
# 2. Fragmentación (Chunking)
    fragmentos = [texto_completo[i:i+1000] for i in range(0, len(texto_completo), 1000)]
                    
# 3. Vectorización y Subida a Pinecone
    for i, fragmento in enumerate(fragmentos):
    vector = obtener_vector(fragmento)
    import time
    time.sleep(3) # Pausa para no saturar Gemini
    id_unico = f"doc_{archivo_pdf.name}_{i}"
    index.upsert(vectors=[{
    "id": id_unico,
    "values": vector,
    "metadata": {"texto": fragmento}
                }])
    st.success("✅ ¡Documento inyectado en la memoria profunda!")
    st.header("🧐 Visión Teológica")
    archivo_imagen = st.file_uploader("Sube una imagen (Papiro, texto, pintura)", type=["jpg", "png", "jpeg"])
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
# --- PROTECCIÓN DE MEMORIA (Ventana Deslizante) ---
    mensajes_recientes = st.session_state.messages[-10:]
    historial = [{"role": "user" if m["role"] == "user" else "model", "parts": m["content"]} for m in mensajes_recientes]
    chat = model.start_chat(history=historial)
# --------------------------------------------------
# Lógica de Visión Multimodal
if archivo_imagen is not None:
    from PIL import Image
    imagen_abierta = Image.open(archivo_imagen)
    respuesta = chat.send_message([prompt_enriquecido, imagen_abierta])
    else:
    respuesta = chat.send_message(prompt_enriquecido)
            
# --- IMPRESIÓN EN PANTALLA (Efecto Telepatía) ---
    import time
    def generador_texto():
    for pedazo in respuesta:
# Desarmamos el bloque en palabras y las imprimimos una por una
    for palabra in pedazo.text.split(" "):
    yield palabra + " "
    time.sleep(0.04) # ⏱️ El latido: 40 milisegundos de pausa visual
            
    texto_completo = st.write_stream(generador_texto())
    st.session_state.messages.append({"role": "assistant", "content": texto_completo})
            
# --- MOTOR DE VOZ (Edge TTS - Microsoft Neuronal Sin Limites) ---
    with st.spinner("🗣️ Sintetizando el sermón completo..."):
    try:
# 1. Limpiamos el texto de asteriscos (Sin límites de corte)
    texto_limpio = texto_completo.replace("*", "").replace("#", "")
                    
    import edge_tts
    import asyncio
    import io
                    
# 2. Creamos la función asíncrona para descargar el audio completo
    async def crear_audio_memoria():
# Usamos la voz de Jorge (Voz neuronal profunda y clara)
    comunicador = edge_tts.Communicate(texto_limpio, "es-MX-JorgeNeural")
    audio_data = b""
    async for chunk in comunicador.stream():
if chunk["type"] == "audio":
    audio_data += chunk["data"]
    return audio_data
                    
# 3. Ejecutamos el motor y guardamos en memoria
    bytes_completos = asyncio.run(crear_audio_memoria())
                    
# 4. Desplegamos el reproductor con el mensaje INTACTO
    audio_bytes = io.BytesIO(bytes_completos)
    st.audio(audio_bytes, format='audio/mp3')
                    
    except Exception as e:
    st.error(f"Error en las cuerdas vocales: {e}")

# 4. Guardar la nueva conversacion en la Memoria
    texto_a_guardar = f"Usuario: {prompt} | Evangelista: {texto_completo[:500]}..."
    vector_a_guardar = obtener_vector(texto_a_guardar)
    id_unico = str(int(time.time())) # Genera un ID basado en la hora actual
            
    index.upsert(vectors=[{
    "id": id_unico,
    "values": vector_a_guardar,
    "metadata": {"texto": texto_a_guardar}
                 }])

    except Exception as e:
    st.error(f"Error en los sistemas: {e}")

# --- MOTOR DE EXPORTACIÓN (Impresora de Sermones) ---
    st.markdown("---")
# 1. Preparamos el documento con un encabezado profesional
    documento_final = f"=== ESTUDIO BÍBLICO: EVANGELISTA IA ===\n\nPREGUNTA DEL USUARIO:\n{prompt}\n\nRESPUESTA TEOLÓGICA:\n{respuesta.text}\n\n======================================="
            
# 2. Generamos el botón de descarga nativo
    st.download_button(
    label="📥 Descargar Estudio Bíblico",
    data=documento_final,
    file_name="sermon_evangelista.txt",
    mime="text/plain"
            )
# ----------------------------------------------------

