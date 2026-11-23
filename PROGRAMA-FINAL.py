import os
import time
import threading
import random
from flask import Flask
import google.generativeai as genai

# --- CONFIGURACION IA ---
# Pon tu API KEY en Render como variable de entorno GOOGLE_API_KEY
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# --- TUS PROMPTS ---
pl = {
    "prompt_ia": """
Eres un experto en creación de tiendas de productos digitales.
Dominio: {dominio}
Tema: {tema}
Título de la tienda: {titulo}
Idioma: {idioma}

Genera una descripción de tienda digital lista para vender, con 3 productos, precios y beneficios.
"""
}

# --- FUNCION QUE CREA LA TIENDA ---
def crear_tienda():
    # Estos datos luego los puedes poner aleatorios o desde Telegram
    dominio = "productosdigitales.com"
    tema = random.choice(["marketing digital", "fitness", "finanzas", "ia"])
    titulo = f"Tienda X402 de {tema}"
    idioma = "español"

    # ESTA ES LA LINEA 45 QUE FALLABA, YA CORREGIDA
    prompt = pl["prompt_ia"].format(dominio=dominio, tema=tema, titulo=titulo, idioma=idioma)
    
    print(f"Generando tienda: {titulo}...")
    try:
        response = model.generate_content(prompt)
        print("--- TIENDA GENERADA ---")
        print(response.text[:500])
        print("-----------------------")
        # Aquí va tu lógica para guardarla / subirla / mandarla a Telegram
    except Exception as e:
        print(f"Error generando: {e}")

# --- BUCLE INFINITO DEL BOT ---
def run_bot():
    print("BOT DE TIENDAS X402 INICIADO...")
    while True:
        crear_tienda()
        print("Esperando 1 hora para la siguiente tienda...")
        time.sleep(3600) # 1 hora

# --- SERVIDOR WEB PARA QUE RENDER NO LO APAGUE ---
app = Flask(__name__)

@app.route('/')
def home():
    return "TIENDA-X402 BOT ACTIVO Y GENERANDO TIENDAS 24/7"

# --- ARRANQUE FINAL ---
if __name__ == "__main__":
    # El bot corre en segundo plano
    threading.Thread(target=run_bot, daemon=True).start()
    # El servidor web corre en el puerto que pide Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
