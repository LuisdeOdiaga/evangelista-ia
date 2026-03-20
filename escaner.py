import requests

print("--- ESCÁNER DE MODELOS DE GOOGLE ---")
API_KEY = input("Pega tu API_KEY aquí y presiona Enter:\n> ")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
try:
    res = requests.get(url)
    datos = res.json()
    
    print("\n✅ MODELOS DISPONIBLES PARA ESTA LLAVE:")
    if 'models' in datos:
        for modelo in datos['models']:
            if 'generateContent' in modelo.get('supportedGenerationMethods', []):
                print(f"👉 {modelo['name'].replace('models/', '')}")
    else:
        print(f"❌ Error de Google: {datos}")
except Exception as e:
    print(f"Error de conexión: {e}")

