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
    st.markdown("### 🔐 Acceso al Búnker Teológico")
    
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

#---- MOTOR VISUAL ---

# 1. PANEL LATERAL (Ingesta y Visión)
with st.sidebar:
    if st.session_state.rol == "admin":
        st.header("📚 Ingesta Teológica")
        archivo_pdf = st.file_uploader("Sube un libro (PDF)", type=["pdf"])
        if archivo_pdf and st.button("🧠 Memorizar"):
            with st.spinner("Inyectando sabiduría..."):
                lector = PyPDF2.PdfReader(archivo_pdf)
                texto = "".join([p.extract_text() for p in lector.pages])
                frags = [texto[i:i+1000] for i in range(0, len(texto), 1000)]
                for i, f in enumerate(frags):
                    v = obtener_vector(f)
                    index.upsert(vectors=[{"id":f"p_{i}","values":v,"metadata":{"texto":f}}])
                st.success("¡Memoria inyectada!")

    st.header("🧐 Visión Teológica")
    archivo_img = st.file_uploader("Analizar imagen sagrada", type=["jpg", "png", "jpeg"])

# 2. CAJA DE CHAT
prompt = st.chat_input("Escribe tu duda teológica profunda...")

if prompt or archivo_img:
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        # A. Búsqueda de Contexto
        v_p = obtener_vector(prompt if prompt else "Imagen analizada")
        res = index.query(vector=v_p, top_k=2, include_metadata=True)
        ctx = "\n".join([m['metadata']['texto'] for m in res['matches']]) if res['matches'] else ""
        
        # B. Generación con ADN (Forzamos estilo)
        chat = model.start_chat(history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]])
        instruccion_estilo = "\n(Responde con encabezados elegantes, usa negritas y un tono solemne de revelación)."
        
        # Lógica de Visión o Texto
        if archivo_img:
            from PIL import Image
            img = Image.open(archivo_img)
            response = model.generate_content([prompt if prompt else "Explica esta imagen teológicamente", img])
        else:
            response = chat.send_message(f"Contexto: {ctx}\n\nPregunta: {prompt}{instruccion_estilo}")
        
        full_res = response.text
        
        # C. EFECTO TELEPATÍA (Palabra por palabra)
        placeholder = st.empty()
        res_progresiva = ""
        for word in full_res.split():
            res_progresiva += word + " "
            placeholder.markdown(res_progresiva + "▌")
            time.sleep(0.05)
        placeholder.markdown(full_res)
        st.session_state.messages.append({"role": "assistant", "content": full_res})

        # D. MOTOR DE VOZ JORGE (Filtro Bíblico)
        with st.spinner("🎙️ Preparando sermón..."):
            import edge_tts, asyncio, re
            # Filtro: Reemplaza "Mateo 13:3" por "Mateo 13 3" para que no lea 13:03 AM
            texto_voz = full_res.replace("*","").replace("#","")
            texto_voz = re.sub(r'(\d+):(\d+)', r'\1 \2', texto_voz) 
            
            async def voz():
                c = edge_tts.Communicate(texto_voz, "es-MX-JorgeNeural", rate="+7%")
                data = b""
                async for chunk in c.stream():
                    if chunk["type"] == "audio": data += chunk["data"]
                return data
            st.session_state.audio_data = asyncio.run(voz())
            st.rerun() # Recarga para mostrar solo la barra de abajo

# 3. ZONA DE EXPORTACIÓN Y AUDIO ÚNICO
if "audio_data" in st.session_state:
    st.markdown("---")
    st.audio(st.session_state.audio_data, format='audio/mp3') # Única barra de audio
    
    doc_final = f"=== ESTUDIO BÍBLICO: {st.session_state.rol.upper()} ===\n\n{st.session_state.messages[-1]['content'] if st.session_state.messages else ''}"
    st.download_button(
        label="📄 Descargar Sermón Proclamado",
        data=doc_final.encode('utf-8-sig'),
        file_name=f"Sermon_Evangelista_{int(time.time())}.txt",
        mime="text/plain"
    )

