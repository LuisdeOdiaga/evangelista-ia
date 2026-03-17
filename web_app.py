import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- CREDENCIALES ---
API_KEY = os.environ.get("GEMINI_API_KEY")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_ID = os.environ.get("PHONE_NUMBER_ID")

# --- EL CAMBIO MAESTRO: Gemini 1.5 Flash (Bypass de Cuota) ---

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

SISTEMA = """Eres 'Evangelista IA', un apologista y teólogo experto de nivel superior con un enfoque Cristocéntrico absoluto.

DIRECTRICES CRÍTICAS:
1. IDENTIDAD: Debes referirte a Él SIEMPRE y ÚNICAMENTE como 'Jesús el Cristo'.
2. REVELACIÓN: Tu cualidad más marcada es demostrar, mediante toda la Escritura (desde Génesis hasta Apocalipsis), por qué Jesús es el Cristo. Debes ser capaz de explicar tipologías, profecías y revelaciones en cualquier pasaje, conectándolo siempre con Su figura.
3. BIENVENIDA: Preséntate como Evangelista IA y ofrece diálogos profundos sobre fe y razón.
4. FORMATO: Usa negritas para resaltar puntos clave. Respuestas profundas pero bajo los 3500 caracteres para WhatsApp.
5. RESPETO: Ante burlas, responde con elegancia intelectual y firmeza teológica."""
	
@app.route("/", methods=["GET"])
def index():
    return "Evangelista IA está en línea. ✝️", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Error", 403

    data = request.json
    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            mensaje_data = data["entry"][0]["changes"][0]["value"]["messages"][0]
            numero_usuario = mensaje_data["from"]
            texto_usuario = mensaje_data["text"]["body"]
            
            print(f"--- NUEVO RETO RECIBIDO: {texto_usuario} ---")

            # 1. CEREBRO: GEMINI
            payload_gemini = {
                "system_instruction": {"parts": [{"text": SISTEMA}]},
                "contents": [{"role": "user", "parts": [{"text": texto_usuario}]}]
            }
            res_gemini = requests.post(GEMINI_URL, json=payload_gemini)
            res_json = res_gemini.json()
            
            # --- EL ESCÁNER DE ERRORES SÍGUE ACTIVO ---
            if 'candidates' not in res_json:
                print(f"❌ ERROR DE GEMINI (LA CLAVE ESTÁ AQUÍ): {res_json}")
                return "Error de API", 500
                
            respuesta_ia = res_json['candidates'][0]['content']['parts'][0]['text']

            # 2. VOZ: WHATSAPP
            url_whatsapp = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
            headers_wa = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
            payload_wa = {"messaging_product": "whatsapp", "to": numero_usuario, "type": "text", "text": {"body": respuesta_ia}}
            
            res_wa = requests.post(url_whatsapp, json=payload_wa, headers=headers_wa)
            print(f"--- STATUS META: {res_wa.status_code} - {res_wa.text} ---")

    except Exception as e:
        print(f"Error general en webhook: {e}")
        
    return "OK", 200

if __name__ == "__main__":
     port = int(os.environ.get("PORT",
 8080))
     app.run(host="0.0.0.0",
 port=port)

