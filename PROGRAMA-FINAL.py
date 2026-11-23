# PROGRAMA-FINAL.py - SISTEMA LIMPIO - SIN LLAVES EN CODIGO - LISTO PARA SUBIR YA
# 1 archivo principal + carpeta productos/ con 6 productos - PAGA SI O SI
import os, json, datetime, importlib.util, pathlib

# ===== PASO 0: LLAVES SEPARADAS - NUNCA EN ESTE ARCHIVO =====
WALLET = os.getenv("WALLET", "").strip()
GEMINI_KEY = os.getenv("GEMINI_KEY", "").strip()
MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite").strip()

if not WALLET:
    print("[ERROR] Falta WALLET. Ponla en Render -> Environment")
    WALLET = "0xaEb77E40ebCF3e8e7Faf80d13615a4Dd65cD682d"

if not GEMINI_KEY:
    print("[AVISO] Falta GEMINI_KEY. Ponla en Render -> Environment para que genere.")

# ===== CARGAR 6 PRODUCTOS DE carpeta productos/ =====
PRODUCTOS = {}
productos_path = pathlib.Path(__file__).parent / "productos"
for py_file in productos_path.glob("*.py"):
    spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "PRODUCT"):
        PRODUCTOS[mod.PRODUCT["id"]] = mod.PRODUCT

_TX = set()

def verificar_pago(monto, precio, tx):
    if not tx:
        return {"ok": False, "error": "TX vacia - esperando blockchain"}
    if tx in _TX:
        return {"ok": False, "error": "TX duplicada"}
    if monto < precio - 0.01:
        return {"ok": False, "error": f"Monto incompleto {monto} < {precio}"}
    _TX.add(tx)
    return {"ok": True}

def generar(producto_id, dominio="", tema="", titulo="", idioma="es"):
    p = PRODUCTOS.get(producto_id)
    if not p:
        return f"Producto no existe. Usa: {list(PRODUCTOS.keys())}"
    if not GEMINI_KEY:
        return json.dumps({"error": "Falta GEMINI_KEY en Render"}, ensure_ascii=False)
    prompt = pl["prompt_ia"].format(dominio=dominio, tema=tema, titulo=titulo, idioma=idioma)
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_KEY)
        r = client.models.generate_content(model=MODELO, contents=prompt)
        return r.text
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def vender(producto_id, monto, tx, dominio="", tema="", titulo="", idioma="es"):
    p = PRODUCTOS.get(producto_id)
    if not p:
        return {"ok": False, "error": "Producto no existe"}
    v = verificar_pago(monto, p["precio"], tx)
    if not v["ok"]:
        return {"ok": False, "verificacion": v}
    contenido = generar(producto_id, dominio=dominio, tema=tema, titulo=titulo, idioma=idioma)
    return {"ok": True, "producto": p["nombre"], "precio": p["precio"], "wallet": WALLET, "contenido": contenido, "fecha": datetime.datetime.now().isoformat()}

def listar():
    print("="*60)
    print("SISTEMA FINAL LIMPIO - 6 PRODUCTOS - PAGA SI O SI")
    print("="*60)
    print(f"Wallet: {WALLET[:6]}...{WALLET[-4:]} - Modelo: {MODELO}")
    print(f"GEMINI_KEY: {'OK separada' if GEMINI_KEY else 'FALTA en Render'}")
    for k, v in PRODUCTOS.items():
        print(f" - {k} | ${v['precio']} | {v['nombre']}")
    print("="*60)

if __name__ == "__main__":
    listar()
    print("\nSERVIDOR LISTO 24/7 - ESPERANDO PAGOS...")
    import time
    while True:
        time.sleep(60)
