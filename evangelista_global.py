import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
import os
import time
import asyncio
from PIL import Image
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

# --- INICIALIZACIÓN DEL SISTEMA DE SEGURIDAD ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "rol" not in st.session_state:
    st.session_state.rol = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# EVANGELIZACION MUNDIAL
# ==========================================

# 1. Inicialización de Memoria de Sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol" not in st.session_state:
    st.session_state.rol = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Pantalla de Login (Si no está autenticado)
if not st.session_state.autenticado:
    st.markdown("### 🌎 Evangelización Mundial")
    
    # Entradas de datos (Fuera del botón para que no se borren)
    usuario_ingresado = st.text_input("👤 Usuario")
    clave_ingresada = st.text_input("🔑 Contraseña", type="password")
    
    # Definición de llaves maestras
    admin_u = os.getenv("ADMIN_USER", "admin")
    admin_p = os.getenv("ADMIN_PASS", "admin")
    guest_u = os.getenv("GUEST_USER", "invitado")
    guest_p = os.getenv("GUEST_PASS", "1234")

    if st.button("Entrar"):
        if usuario_ingresado == admin_u and clave_ingresada == admin_p:
            st.session_state.autenticado = True
            st.session_state.rol = "admin"
            st.rerun()
        elif usuario_ingresado == guest_u and clave_ingresada == guest_p:
            st.session_state.autenticado = True
            st.session_state.rol = "invitado"
            st.rerun()
        else:
            st.error("🚨 Credenciales incorrectas.")
    
    st.stop() # Detiene la ejecución aquí si no hay login exitoso

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
    st.chat_message(message["role"]).markdown(message["content"])

# ## --- MOTOR VISUAL ---

# 1. PANEL LATERAL (Ingesta y Visión)
with st.sidebar:
    if st.session_state.rol == "admin":
        st.header("📚 Ingesta Teológica")
        archivo_pdf = st.file_uploader("Sube un libro (PDF)", type=["pdf"])
        if archivo_pdf and st.button("🧠 Memorizar"):
            with st.spinner("Desmenuzando el pergamino..."):
                try:
                    lector = PyPDF2.PdfReader(archivo_pdf)
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

    st.header("🧐 Visión Teológica")
    archivo_img = st.file_uploader("Analizar imagen sagrada", type=["jpg", "png", "jpeg"])

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

# A. Imprimir los mensajes anteriores (¡Para que no desaparezcan!)
for mensaje in st.session_state.messages:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# B. La Caja de Entrada
prompt = st.chat_input("Escribe tu duda teológica profunda...")

if prompt or archivo_img:
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    with st.chat_message("assistant"):
        # --- 1. Traductor de Memoria ---
        historial_gemini = []
        for m in st.session_state.messages[:-1]:
            rol_gemini = "model" if m["role"] == "assistant" else "user"
            historial_gemini.append({"role": rol_gemini, "parts": [m["content"]]})
        
        chat = model.start_chat(history=historial_gemini)
        
        # --- 2. Búsqueda y Generación ---
        v_p = obtener_vector(prompt if prompt else "Imagen analizada")
        res = index.query(vector=v_p, top_k=2, include_metadata=True)
        ctx = "\n".join([m['metadata']['texto'] for m in res['matches']]) if res['matches'] else ""
        
        instruccion_estilo = "\n(Responde con encabezados elegantes, usa negritas y un tono solemne)."
        
        if archivo_img:
            from PIL import Image
            img = Image.open(archivo_img)
            response = model.generate_content([prompt if prompt else "Explica esta imagen", img])
        else:
            response = chat.send_message(f"Contexto: {ctx}\n\nPregunta: {prompt}{instruccion_estilo}")
        
        full_res = response.text
        
        # --- 3. Efecto Telepatía ---
        import time
        placeholder = st.empty()
        res_progresiva = ""
        for word in full_res.split():
            res_progresiva += word + " "
            placeholder.markdown(res_progresiva + "▌")
            time.sleep(0.05)
        placeholder.markdown(full_res)
        st.session_state.messages.append({"role": "assistant", "content": full_res})

        # --- 4. Motor de Voz (Blindaje Anti-Crash) ---
        with st.spinner("🎙️ Preparando sermón..."):
            import edge_tts, asyncio, re
            texto_voz = full_res.replace("*","").replace("#","")
            texto_voz = re.sub(r'(\d+):(\d+)', r'\1 \2', texto_voz) 
            
            async def voz():
                c = edge_tts.Communicate(texto_voz, "es-MX-JorgeNeural", rate="+7%")
                data = b""
                async for chunk in c.stream():
                    if chunk["type"] == "audio": data += chunk["data"]
                return data
                
            # El truco para que el servidor no explote con la segunda pregunta
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            st.session_state.audio_data = loop.run_until_complete(voz())

# ==========================================
# 3. ZONA DE EXPORTACIÓN Y AUDIO (Fija al fondo)
# ==========================================
if "audio_data" in st.session_state:
    st.markdown("---")
    st.audio(st.session_state.audio_data, format='audio/mp3')
    
    if st.session_state.messages:
        ultimo_mensaje = st.session_state.messages[-1]['content']
        
        # --- LA CAJA FUERTE VISUAL (Matando el Fantasma) ---
        with st.expander("📥 Opciones de Descarga del Último Sermón", expanded=True):
            
            # --- MOTOR DE IMPRENTA PDF OPTIMIZADO ---
            import re
            import time
            from io import BytesIO
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
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

            # --- BOTONES DE DESCARGA DENTRO DE LA CAJA ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📄 Descargar en TXT",
                    data=f"=== ESTUDIO BÍBLICO ===\n\n{ultimo_mensaje}".encode('utf-8-sig'),
                    file_name=f"Sermon_{int(time.time())}.txt",
                    mime="text/plain"
                )
                
        # ---------------- PDF ----------------
        with col2:
            st.download_button(
                label="📕 Descargar en PDF",
                data=st.session_state.pdf_generado,
                file_name="Sermon.pdf",
                mime="application/octet-stream", # <--- EL BYPASS HACKER
                key="download_pdf_btn"
            )

