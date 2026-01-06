import streamlit as st
import requests
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="¿Cómo Pagar? Vzla", page_icon="💸", layout="centered")

# 2. ESTILOS CSS
st.markdown("""
<style>
    .main { background-color: #f4f7f6; }
    .card-amarilla { background-color: #FFCC00; padding: 20px; border-radius: 15px; border: 4px solid #FBC02D; margin-bottom: 15px; color: #1a1a1a !important; }
    .card-azul { background-color: #0056b3; padding: 20px; border-radius: 15px; border: 4px solid #004494; margin-bottom: 15px; color: #ffffff !important; }
    .card-roja { background-color: #d32f2f; padding: 20px; border-radius: 15px; border: 4px solid #b71c1c; margin-bottom: 15px; color: #ffffff !important; }
    .badge-mejor { background-color: #2e7d32; color: white !important; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.85em; border: 1px solid white; }
    .card-amarilla span, .card-amarilla p { color: #1a1a1a !important; }
    .card-azul span, .card-azul p { color: #ffffff !important; }
    .card-roja span, .card-roja p { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE DATOS ---
@st.cache_data(ttl=300)
def obtener_tasa_binance():
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {"page": 1, "rows": 1, "asset": "USDT", "tradeType": "BUY", "fiat": "VES"}
        response = requests.post(url, json=payload, timeout=5)
        return float(response.json()['data'][0]['adv']['price'])
    except: return 570.00

# --- CARGA DE DATOS ---
t_bin_auto = obtener_tasa_binance()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    t_bcv = st.number_input("Tasa BCV Oficial (Bs/$)", value=308.15460000, format="%.2f")
    t_binance = st.number_input("Tasa Binance P2P (Bs/$)", value=t_bin_auto, format="%.2f")
    tasa_cambista_calculada = t_binance * 0.80
    t_cambista = st.number_input("Tasa Cambista", value=tasa_cambista_calculada, format="%.2f")
    if st.button("🔄 Actualizar Binance", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- CUERPO PRINCIPAL ---
st.markdown("<h1 style='text-align: center;'>🇻🇪 ¿Cómo Pagar?</h1>", unsafe_allow_html=True)

st.subheader("📝 Datos de la Tienda")
precio_efectivo = st.number_input("Precio en Efectivo ($)", min_value=0.0, value=0.0)

metodo_cobro = st.radio(
    "¿Cómo te dijeron el precio en Bolívares?",
    ["Monto directo en Bs", "Monto en $ a tasa BCV"],
    horizontal=True
)

if metodo_cobro == "Monto directo en Bs":
    total_bolivares_pedidos = st.number_input("Monto total en Bolívares (Bs)", min_value=0.0, value=0.0)
else:
    precio_en_bs_equiv = st.number_input("Precio equivalente en $ (a tasa BCV)", min_value=0.0, value=0.0)
    total_bolivares_pedidos = precio_en_bs_equiv * t_bcv

# CÁLCULOS
tasa_tienda_real = total_bolivares_pedidos / precio_efectivo if precio_efectivo > 0 else 0
costo_efe_usd = precio_efectivo * 1.03
costo_bin_usd = total_bolivares_pedidos / t_binance if t_binance > 0 else 0
costo_cam_usd = total_bolivares_pedidos / t_cambista if t_cambista > 0 else 0

# --- RENDERIZADO DE TARJETAS ---
st.divider()
st.subheader("📊 Comparativa de Costos")

opciones = [
    {"n": "Efectivo (Dólares)", "usd": costo_efe_usd, "ves": costo_efe_usd * t_bcv, "style": "card-amarilla", "tag": "Incluye 3% IGTF", "icon": "💵"},
    {"n": "Bolívares (Binance)", "usd": costo_bin_usd, "ves": total_bolivares_pedidos, "style": "card-azul", "tag": f"Tasa: {t_binance:.2f}", "icon": "📱"},
    {"n": "Bolívares (Cambista)", "usd": costo_cam_usd, "ves": total_bolivares_pedidos, "style": "card-roja", "tag": f"Tasa: {t_cambista:.2f}", "icon": "💱"}
]

# Rankeo de opciones válidas
validas = [o for o in opciones if o["usd"] > 0]
rankeadas = sorted(validas, key=lambda x: x["usd"])

for opc in opciones:
    mejor = len(rankeadas) > 0 and opc["n"] == rankeadas[0]["n"]
    badge = f'<span class="badge-mejor">⭐ LA MEJOR</span>' if mejor else ""
    card_html = (
        f'<div class="{opc["style"]}">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
        f'<span style="font-size:1.1em;font-weight:bold;">{opc["icon"]} {opc["n"]}</span>{badge}</div>'
        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<div><p style="font-size:2.2em;font-weight:900;margin:0;padding:0;">${opc["usd"]:.2f}</p>'
        f'<p style="font-size:1.1em;font-weight:600;margin:0;opacity:0.9;">{opc["ves"]:,.2f} Bs</p></div>'
        f'<span style="font-size:0.85em;font-weight:500;text-align:right;">{opc["tag"]}</span></div></div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

# --- RECOMENDACIÓN FINAL (RANKING COMPLETO) ---
if len(rankeadas) >= 1 and precio_efectivo > 0:
    st.divider()
    st.markdown("### 🏆 Veredicto de Ahorro")
    
    # 1era Opción
    st.success(f"**🥇 Plan A (Ideal):** Paga con **{rankeadas[0]['n']}**. Costo: **${rankeadas[0]['usd']:.2f}**")
    
    # 2da Opción (Si existe)
    if len(rankeadas) >= 2:
        dif_2da = rankeadas[1]['usd'] - rankeadas[0]['usd']
        st.info(f"**🥈 Plan B (Alternativa):** Si no puedes usar la primera, usa **{rankeadas[1]['n']}**. Pagas **${dif_2da:.2f}** adicionales.")
        
    # Análisis de Efectivo (Punto de Empate)
    if rankeadas[0]["n"] != "Efectivo (Dólares)":
        tasa_empate = total_bolivares_pedidos / costo_efe_usd
        with st.expander("🤔 ¿Cuándo convendría usar el Efectivo?"):
            st.write(f"Para que el Efectivo pase a ser la mejor opción, la tasa de cambio debería bajar hasta **{tasa_empate:.2f} Bs/$**.")

st.caption(f"Actualizado: {datetime.now().strftime('%H:%M:%S')}")