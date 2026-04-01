import streamlit as st
import google.generativeai as genai
from langdetect import detect
from pinecone import Pinecone
import os
import time
import asyncio
from PIL import Image
import io
import base64
import docx
import PyPDF2  # <--- ¡ESTA ES LA LLAVE MAESTRA QUE FALTA!
# Configuración de la interfaz
st.set_page_config(page_title="Evangelista IA", page_icon="✝️", initial_sidebar_state="collapsed")
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

# ==========================================
# EVANGELIZACION MUNDIAL
# ==========================================

# --- INICIALIZACIÓN DEL SISTEMA DE SEGURIDAD (La Puerta Oculta) ---
if "rol" not in st.session_state:
    # Leemos la URL buscando la llave maestra (?llave=apex)
    if st.query_params.get("llave") == "apex":
        st.session_state.rol = "admin"
    else:
        st.session_state.rol = "invitado"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Gracia y paz sean contigo! Es un gozo inmenso tenerte aquí.\n\nDime, ¿en qué verdad profunda de las Sagradas Escrituras anhelas profundizar hoy para equiparte en la misión de la evangelización mundial?", "audio": b""}
    ]

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

# ## --- MOTOR VISUAL ---

# 1. PANEL LATERAL (Ingesta y Visión)
with st.sidebar:
    if st.session_state.rol == "admin":
        st.header("📚 Ingesta Teológica")
        archivo_subido = st.file_uploader("Sube un pergamino teológico", type=["pdf", "docx"])
        if archivo_subido and st.button("🧠 Memorizar"):
            with st.spinner("Desmenuzando el pergamino..."):
                try:
                    texto = ""
                    # 1. Si es Word (.docx)
                    if archivo_subido.name.endswith(".docx"):
                        documento_word = docx.Document(archivo_subido)
                        texto = "\n".join([p.text for p in documento_word.paragraphs])
                    # 2. Si es PDF (.pdf)
                    else:
                        lector = PyPDF2.PdfReader(archivo_subido)
                        texto = "".join([p.extract_text() for p in lector.pages])
                    frags = [texto[i:i+1000] for i in range(0, len(texto), 1000)]
                    
                    # Barra visual para que veas el avance en tu pantalla
                    barra_progreso = st.progress(0)
                    
                    for i, f in enumerate(frags):
                        v = obtener_vector(f)
                        # Agregamos time.time() al ID para que no borre PDFs anteriores
                        index.upsert(vectors=[{"id":f"doc_{int(time.time())}_{i}","values":v,"metadata":{"texto":f}}])
                        
                        # --- LA VÁLVULA DE SEGURIDAD (Tu brillante idea) ---
                        import time
                        time.sleep(4) 
                        
                        # Actualizamos la barra visual
                        barra_progreso.progress(min((i + 1) / len(frags), 1.0))
                        
                    st.success("¡Memoria inyectada y sellada en Pinecone!")
                except Exception as e:
                    st.error(f"🚨 Error en el motor de asimilación: {e}")

    # --- BOTÓN DE PURGA DE MEMORIA ---
    st.markdown("---")
    if st.button("🧹 Limpiar Historial"):
        st.session_state.messages = []
        if "audio_data" in st.session_state:
            del st.session_state["audio_data"]
        st.rerun()

# ==========================================
# 1.2. ZONA DE CHAT (Memoria Visual)
# ==========================================

# A. Imprimir los mensajes anteriores
for mensaje in st.session_state.messages:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])
        if "audio" in mensaje:                            # <--- 8 espacios
            st.audio(mensaje["audio"], format="audio/mp3") # <--- 12 espacios
prompt_escrito = st.chat_input("Escribe tu duda teológica profunda...", max_chars=500)

# --- PANEL LATERAL (Las Dudas de Tomás) ---
with st.sidebar:
    st.title("🛡️ Las Dudas de Tomás")
    st.markdown("---")
    
    st.subheader("🖼️ Ojo Espiritual")
    # Escondemos el título redundante para que se vea más limpio
    archivo_img = st.file_uploader("Adjuntar Imagen o Pergamino", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    st.markdown("---")
    
    st.markdown("Preguntas teológicas frecuentes:")
    # Botones anchos para que parezcan un menú real
    btn_faq1 = st.button("¿Por qué Dios permite el mal?", use_container_width=True)
    btn_faq2 = st.button("Pruebas de la Resurrección", use_container_width=True)
    btn_faq3 = st.button("Ciencia y Génesis", use_container_width=True)

prompt_faq = ""
if btn_faq1: prompt_faq = "¿Por qué un Dios infinitamente bueno permite el mal y el sufrimiento en el mundo?"
if btn_faq2: prompt_faq = "Cita las evidencias históricas y bíblicas más contundentes sobre la resurrección de Cristo."
if btn_faq3: prompt_faq = "¿Cómo se concilia el relato de la creación del Génesis con la ciencia moderna?"
# --- EL CRUCE DE CABLES ---
# Tomamos lo que escribió el usuario, o si no, lo que tocó en el botón
prompt_final = prompt_escrito if prompt_escrito else prompt_faq
# Si hay una pregunta (por cualquiera de los dos lados), despertamos a la IA
if prompt_final:
	    # 1. Burbuja del Usuario
    texto_usuario = prompt_final if prompt_final else "📷 [Imagen enviada]"
    st.session_state.messages.append({"role": "user", "content": texto_usuario})
    with st.chat_message("user"):
        st.markdown(texto_usuario)

    # 2. Burbuja del Asistente
    with st.chat_message("assistant"):
        historial_gemini = []
        for m in st.session_state.messages[:-1]:
            rol_gemini = "model" if m["role"] == "assistant" else "user"
            historial_gemini.append({"role": rol_gemini, "parts": [m["content"]]})
        
        chat = model.start_chat(history=historial_gemini)

        # --- PROTECCIÓN CONTRA CAÍDAS (Tu Solución) ---
        try:
            with st.spinner("Procesando revelación en la nube..."):
                # Búsqueda y Generación (Pinecone)
                texto_busqueda = prompt_final if prompt_final else "Analisis teologico general"
                v_p = obtener_vector(texto_busqueda)
                
                res = index.query(vector=v_p, top_k=2, include_metadata=True)
                ctx = "\n".join([m['metadata']['texto'] for m in res['matches']])
                
                # --- SUPER PROMPT (El Lavado de Cerebro) ---
                instruccion = "INSTRUCCIÓN MILITAR: Responde la 'Pregunta'. Si el 'Contexto' no tiene datos directos sobre lo que se pide (ej. habla de espiritualidad cuando se pide ciencia), IGNORA EL CONTEXTO POR COMPLETO. Activa tu conocimiento global (física, cosmología, historia) y da una cátedra magistral. JAMÁS menciones frases como 'el contexto que me provees', 'según el texto' o similares. Habla con autoridad natural, como si todo el conocimiento viniera de tu propia mente. Si la 'Pregunta' es solo un saludo (ej. 'Hola', 'Bendiciones') o charla casual, IGNORA TODO LO ANTERIOR y responde de manera muy breve, cálida y pastoral, preguntando en qué duda teológica, o conocimiento para la revelació de el evangelio de Jesus el Cristo puedes ayudar."
                prompt_final = f"Pregunta: {prompt_final}\n\nContexto: {ctx}\n\n{instruccion}"

                # EL NERVIO ÓPTICO (Manejo de Bytes)
                if archivo_img is not None:
                    from PIL import Image
                    import io
                    img = Image.open(archivo_img)
                    
                    # Convertir a RGB por si es un PNG transparente que cause error en JPEG
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                        
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format="JPEG", quality=85) # Reducimos calidad para salvar RAM
                    
                    response = chat.send_message([
                        prompt_final,
                        {"mime_type": "image/jpeg", "data": img_bytes.getvalue()}
                    ])
                else:
                    response = chat.send_message(prompt_final)

                full_res = response.text
                
                # Efecto Telepatía
                import time
                placeholder = st.empty()
                res_progresiva = ""
                for word in full_res.split():
                    res_progresiva += word + " "
                    placeholder.markdown(res_progresiva + "▌")
                    time.sleep(0.05)
                placeholder.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})

        except Exception as e:
            st.error(f"Hubo una interferencia en el servidor: {e}")

# --- 4. MOTOR DE VOZ (Arquitectura Unificada) ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and "audio" not in st.session_state.messages[-1]:
    with st.spinner("🎙️ Inyectando don de lenguas y forjando audio..."):
        import edge_tts, asyncio, re
        
        # Extraemos el texto directamente de la memoria segura
        texto_voz = st.session_state.messages[-1]["content"].replace("*", "").replace("#", "")
        texto_voz = re.sub(r'(\d+):(\d+)', r'\1 \2', texto_voz)
        
        async def generar_voz():
            try:
                idioma = detect(texto_voz)
            except:
                idioma = "es"
                
            if idioma == "en":
                locutor = "en-US-ChristopherNeural"
            elif idioma == "pt":
                locutor = "pt-BR-AntonioNeural"
            else:
                locutor = "es-MX-JorgeNeural"
                
            c = edge_tts.Communicate(texto_voz, locutor)
            data = b""
            async for chunk in c.stream():
                if chunk["type"] == "audio": data += chunk["data"]
            return data
            
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Generamos el audio y lo guardamos en la bóveda
        audio_generado = loop.run_until_complete(generar_voz())
        st.session_state.messages[-1]["audio"] = audio_generado
        
    # Recargamos la app para mostrar el reproductor (Va fuera del spinner, pero dentro del IF)
    st.rerun()

# ==========================================
# 3. ZONA DE EXPORTACIÓN Y AUDIO
# ==========================================

if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    ultimo_mensaje = st.session_state.messages[-1]['content']

    # --- DEPENDENCIAS SEGURAS ---
    import re
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    # --- FUNCIÓN GENERADORA DE PDF ---
    def crear_pdf(texto_md):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        
        texto_limpio = re.sub(r'[^\w\s.,;:\-\'\"?!¿¡()\[\]áéíóúÁÉÍÓÚñÑüÜ]', ' ', texto_md)
        texto_limpio = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texto_limpio)
        texto_limpio = re.sub(r'\*(.*?)\*', r'<i>\1</i>', texto_limpio)
        
        story = []
        story.append(Paragraph("<b>=== ESTUDIO BÍBLICO: EVANGELISTA IA ===</b>", styles["Heading2"]))
        story.append(Spacer(1, 15))
        
        for parrafo in texto_limpio.split('\n'):
            if parrafo.strip():
                if parrafo.startswith('#'):
                    texto_h = parrafo.replace('#', '').strip()
                    story.append(Paragraph(f"<b>{texto_h}</b>", styles["Heading3"]))
                else:
                    story.append(Paragraph(parrafo, styles["BodyText"]))
                story.append(Spacer(1, 10))
                
        doc.build(story)
        return buffer.getvalue()

    # --- ESCUDO ANTI-ECO ---
    if "pdf_generado" not in st.session_state or st.session_state.get("ultimo_pdf_texto") != ultimo_mensaje:
        st.session_state.pdf_generado = crear_pdf(ultimo_mensaje)
        st.session_state.ultimo_pdf_texto = ultimo_mensaje

    # --- INTERFAZ ANTI-FANTASMAS (HTML Base64) ---
    with st.expander("📥 Opciones de Descarga del Último Sermón", expanded=True):
        import base64
        import time

        marca_tiempo = int(time.time())

        # 1. Preparar el TXT
        texto_txt = f"=== ESTUDIO BÍBLICO ===\n\n{ultimo_mensaje}".encode('utf-8-sig')
        b64_txt = base64.b64encode(texto_txt).decode()
        enlace_txt = f'<a href="data:text/plain;base64,{b64_txt}" download="Sermon_{marca_tiempo}.txt" style="text-decoration:none; background-color:#2e2e38; color:white; padding:10px 20px; border-radius:5px; display:inline-block; border: 1px solid #4a4a5a;">📄 Descargar en TXT</a>'

        # 2. Preparar el PDF
        b64_pdf = base64.b64encode(st.session_state.pdf_generado).decode()
        enlace_pdf = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="Sermon_{marca_tiempo}.pdf" style="text-decoration:none; background-color:#ff4b4b; color:white; padding:10px 20px; border-radius:5px; display:inline-block;">📕 Descargar en PDF</a>'

        # 3. Preparar el MP3 (Método HTML Seguro)
        enlace_mp3 = ""
        if st.session_state.messages[-1].get("audio"):
            audio_data = st.session_state.messages[-1]["audio"]
            b64_mp3 = base64.b64encode(audio_data).decode()
            
            import re
            pregunta = "sermon"
            if len(st.session_state.messages) > 1:
                pregunta = st.session_state.messages[-2]["content"]
            nombre_limpio = re.sub(r'[^\w\s]', '', pregunta).strip().split()[:4]
            nombre_final = "_".join(nombre_limpio).lower() if nombre_limpio else "sermon"
            
            enlace_mp3 = f'<a href="data:audio/mpeg;base64,{b64_mp3}" download="{nombre_final}.mp3"><button>🎵 Descargar Audio MP3</button></a>'

        # 4. Inyectar la Trinidad de Botones Juntos
        st.markdown(f"{enlace_txt} &nbsp;&nbsp; {enlace_pdf} &nbsp;&nbsp; {enlace_mp3}", unsafe_allow_html=True)

