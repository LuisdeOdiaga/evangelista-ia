from flask import Flask, request, render_template_string
import requests
import json
import os
app = Flask(__name__)

# =========================================================
# Evangelista IA v3.0 - Arquitectura Full-Stack Pura
# =========================================================

API_KEY = os.environ.get("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

instruccion_sistema = """
Eres un evangelista y un apologista cristiano de nivel experto. 
Tienes un conocimiento absoluto de la Biblia, la teologia y la filosofia. 
Tu mision es defender la fe cristiana ante cualquier argumento cientifico, filosofico o esceptico.
Responde con la sabiduria de Jesucristo: combinando rigor logico impecable, gracia, mansedumbre y firmeza. 
Desarticula las falacias con argumentos solidos. Manten respuestas claras y persuasivas.
"""

# Frontend: Interfaz visual con HTML, CSS y JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Evangelista IA</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f0f2f5; }
        #chat { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); height: 50vh; overflow-y: auto; display: flex; flex-direction: column; gap: 10px;}
        .msg { padding: 12px 15px; border-radius: 8px; max-width: 85%; line-height: 1.4; }
        .user { background: #d1e7dd; align-self: flex-end; border-bottom-right-radius: 0; }
        .ia { background: #e2e3e5; align-self: flex-start; border-bottom-left-radius: 0; }
        #input-box { max-width: 600px; margin: 20px auto; display: flex; gap: 10px; }
        input { flex: 1; padding: 15px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px;}
        button { padding: 15px 25px; background: #0b5ed7; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px;}
        button:hover { background: #0a58ca; }
    </style>
</head>
<body>
    <h2 style="text-align: center; color: #333;">Evangelista IA ✝️</h2>
    <div id="chat">
        <div class="msg ia"><b>IA:</b> Hola. Soy el motor apologético. ¿Qué duda teológica o científica tienes hoy?</div>
    </div>
    <div id="input-box">
        <input type="text" id="mensaje" placeholder="Escribe tu argumento aquí...">
        <button onclick="enviar()">Preguntar</button>
    </div>

    <script>
        function enviar() {
            var input = document.getElementById('mensaje');
            var msg = input.value;
            if(!msg) return;
            
            var chat = document.getElementById('chat');
            chat.innerHTML += '<div class="msg user"><b>Tú:</b> ' + msg + '</div>';
            input.value = 'Pensando...';
            input.disabled = true;
            
            fetch('/preguntar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({pregunta: msg})
            })
            .then(response => response.json())
            .then(data => {
                // Convertimos los saltos de linea en etiquetas HTML para que se vea bien
                var formato_html = data.respuesta.replace(/(?:\\r\\n|\\r|\\n)/g, '<br>');
                chat.innerHTML += '<div class="msg ia"><b>Evangelista IA:</b><br>' + formato_html + '</div>';
                chat.scrollTop = chat.scrollHeight;
                input.value = '';
                input.disabled = false;
                input.focus();
            })
            .catch(error => {
                chat.innerHTML += '<div class="msg ia" style="color:red;">Error de conexión.</div>';
                input.value = '';
                input.disabled = false;
            });
        }
    </script>
</body>
</html>
"""

# Backend: El servidor que entrega la pagina web
@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

# Backend: El puente que conecta el Javascript del navegador con la API de Google
@app.route("/preguntar", methods=["POST"])
def preguntar():
    datos = request.json
    mensaje = datos.get("pregunta", "")
    
    payload = {
        "system_instruction": {"parts": [{"text": instruccion_sistema}]},
        "contents": [{"parts": [{"text": mensaje}]}]
    }
    
    try:
        respuesta = requests.post(URL, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        if respuesta.status_code == 200:
            texto_ia = respuesta.json()['candidates'][0]['content']['parts'][0]['text']
            return {"respuesta": texto_ia}
        else:
            return {"respuesta": f"El servidor rechazó la petición. Código: {respuesta.status_code}"}
    except Exception as e:
        return {"respuesta": f"Fallo interno del servidor: {str(e)}"}

 # ==========================================
 # CONEXIÓN OMNICANAL: WEBHOOK DE WHATSAPP
 # ==========================================
 # Esta es nuestra contraseña inventada para que Meta nos reconozca
VERIFY_TOKEN = "Evangelista_Secreto_2026"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # 1. FASE DE VERIFICACIÓN (Meta tocando la puerta)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("¡WEBHOOK VERIFICADO POR META!")
            return challenge, 200
        else:
            return "Error de validacion", 403

    # 2. FASE DE RECEPCIÓN (Aquí llegarán los mensajes en el futuro)
    elif request.method == "POST":
        data = request.get_json()
        print("Mensaje recibido de WhatsApp:", data)
        return "OK", 200
    if __name__ == "__main__":
            print("=====================================================")
            print(" SERVIDOR ACTIVO: Abre tu navegador web y entra a:")
            print(" http://127.0.0.1:8080")
            print("=====================================================")
            app.run(host="0.0.0.0", port=8080)

