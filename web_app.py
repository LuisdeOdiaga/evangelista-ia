import os
import requests
import json
from flask import Flask, request

app = Flask(__name__)

# --- CONFIGURACIÓN DE PODER ---
# Estas variables se leen directamente desde el panel de Render
API_KEY = os.environ.get("GEMINI_API_KEY")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_ID = os.environ.get("PHONE_NUMBER_ID")

# Endpoint de Gemini 2.0 Flash (Vanguardia 2026)
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# Instrucción Maestra: El ADN de tu IA
SISTEMA = """Eres un evangelista y un apologista cristiano de nivel experto. 
Tienes conocimiento absoluto de la Biblia, teología y filosofía. Tu misión es defender 
la fe ante cualquier argumento científico con rigor lógico impecable y la sabiduría de Jesucristo.
Desarticula falacias con argumentos sólidos. Mantén respuestas claras pero profundas."""

@app.route("/", methods=["GET"])
def index():
    return "Evangelista IA está en línea y operando. ✝️", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # 1. Fase de Verificación (Handshake con Meta)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Error de validación", 403

    # 2. Fase de Recepción y Respuesta
    data = request.json
    try:
        # Extraemos el mensaje si existe
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            mensaje_data = data["entry"][0]["changes"][0]["value"]["messages"][0]
            numero_usuario = mensaje_data["from"]
            texto_usuario = mensaje_data["text"]["body"]
            
            print(f"--- NUEVO RETO RECIBIDO: {texto_usuario} ---")

            # LLAMADA AL CEREBRO (GEMINI)
            payload_gemini = {
                "system_instruction": {"parts": [{"text": SISTEMA}]},
                "contents": [{"parts": [{"text": texto_usuario}]}]
            }
            
            res_gemini = requests.post(GEMINI_URL, json=payload_gemini)
            res_json = res_gemini.json()
            
            # Extraer el texto generado por la IA
            respuesta_ia = res_json['candidates'][0]['content']['parts'][0]['text']

            # LLAMADA A LA VOZ (WHATSAPP CLOUD API)
            url_whatsapp = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
            headers_wa = {
                "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                "Content-Type": "application/json"
            }
            payload_wa = {
                "messaging_product": "whatsapp",
                "to": numero_usuario,
                "type": "text",
                "text": {"body": respuesta_ia}
            }
            
            requests.post(url_whatsapp, json=payload_wa, headers=headers_wa)
            print(f"--- RESPUESTA ENVIADA A {numero_usuario} ---")

    except Exception as e:
        print(f"Error procesando el webhook: {e}")
        
    return "OK", 200

if __name__ == "__main__":
    # Puerto dinámico para Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

