import streamlit as st
import requests
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="¿Cómo Pagar? Vzla",
    page_icon="💸",
    layout="centered"
)

# 2. ESTILOS CSS (Limpios para evitar fugas de texto)
st.markdown("""
<style>
    .main { background-color: #f4f7f6; }
    .card-amarilla {
        background-color: #FFCC00;
        padding: 20px;
        border-radius: 15px;
        border: 4px solid #FBC02D;
        margin-bottom: 15px;
        color: #1a1a1a !important;
    }
    .card-azul {
        background-color: #0056b3;
        padding: 20px;
        border-radius: 15px;
        border: 4px solid #004494;
        margin-bottom: 15px;
        color: #ffffff !important;
    }
    .card-roja {
        background-color: #d32f2f;
        padding: 20px;
        border-radius: 15px;
        border: 4px solid #b71c1c;
        margin-bottom: 15px;
        color: #ffffff !important;
    }
    .badge-mejor {
        background-color: #2e7d32;
        color: white !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85em;
        border: 1px solid white;
    }
    /* Forzar visibilidad de textos internos */
    .card-amarilla span, .card-amarilla p { color: #1a1a1a !important; }
    .card-azul span, .card-azul p { color: #ffffff !important; }
    .card-roja span, .card-roja p { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE DATOS ---
@st.cache_data(ttl=3600)
def obtener_tasas_bcv():
    return {"usd": 47.60, "eur": 51.20}

@st.cache_data(ttl=300)
def obtener_tasa_binance():
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {"page": 1, "rows": 1, "asset": "USDT", "tradeType": "BUY", "fiat": "VES"}
        response = requests.post(url, json=payload, timeout=5)
        return float(response.json()['data'][0]['adv']['price'])
    except:
        return 56.50

# --- CARGA DE DATOS ---
tasas_bcv = obtener_tasas_bcv()
t_bin_auto = obtener_tasa_binance()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    t_bcv = st.number_input("Tasa Dólar BCV", value=tasas_bcv["usd"], format="%.2f")
    t_euro = st.number_input("Tasa Euro BCV", value=tasas_bcv["eur"], format="%.2f")
    t_binance = st.number_input("Tasa Binance P2P", value=t_bin_auto, format="%.2f")
    t_cambista = st.number_input("Tasa Cambista", value=t_binance - 0.40, format="%.2f")
    if st.button("🔄 Actualizar Tasas", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- CUERPO PRINCIPAL ---
st.markdown("<h1 style='text-align: center;'>🇻🇪 ¿Cómo Pagar?</h1>", unsafe_allow_html=True)

col_m1, col_m2 = st.columns([2, 1])
with col_m1:
    moneda_ref = st.selectbox("Moneda del precio:", ["Dólares ($)", "Euros (€)", "Bolívares (Bs)"])
with col_m2:
    precio_ref = st.number_input("Precio:", min_value=0.0, value=10.0)

# Lógica de conversión
if "Dólares" in moneda_ref:
    ves_tienda = precio_ref * t_bcv
    usd_equivalente = precio_ref
elif "Euros" in moneda_ref:
    ves_tienda = precio_ref * t_euro
    usd_equivalente = (precio_ref * t_euro) / t_bcv
else:
    ves_tienda = precio_ref
    usd_equivalente = precio_ref / t_bcv

costo_efe = usd_equivalente * 1.03
costo_bin = ves_tienda / t_binance
costo_cam = ves_tienda / t_cambista

# --- RENDERIZADO DE TARJETAS (ESTRUCTURA SIN SALTOS DE LÍNEA) ---
st.divider()
st.subheader("📊 Comparativa de Costos")

opciones = [
    {"n": "Efectivo (Dólares)", "c": costo_efe, "style": "card-amarilla", "tag": "Incluye 3% IGTF", "icon": "💵"},
    {"n": "Bolívares (Binance)", "c": costo_bin, "style": "card-azul", "tag": f"Tasa: {t_binance}", "icon": "📱"},
    {"n": "Bolívares (Cambista)", "c": costo_cam, "style": "card-roja", "tag": f"Tasa: {t_cambista}", "icon": "💱"}
]

opciones = sorted(opciones, key=lambda x: x["c"])

for i, opc in enumerate(opciones):
    mejor = i == 0
    badge = f'<span class="badge-mejor">⭐ LA MEJOR</span>' if mejor else ""
    
    # IMPORTANTE: Todo el HTML en una sola línea para que Streamlit no lo rompa
    card_html = (
        f'<div class="{opc["style"]}">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">'
        f'<span style="font-size:1.1em;font-weight:bold;">{opc["icon"]} {opc["n"]}</span>{badge}</div>'
        f'<div style="display:flex;justify-content:space-between;align-items:baseline;">'
        f'<p style="font-size:2.2em;font-weight:900;margin:0;padding:0;">${opc["c"]:.2f}</p>'
        f'<span style="font-size:0.85em;font-weight:500;">{opc["tag"]}</span></div></div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

# Mensaje de éxito
ahorro = opciones[1]["c"] - opciones[0]["c"]
if ahorro > 0:
    st.success(f"💡 Pagando con **{opciones[0]['n']}** ahorras **${ahorro:.2f}** frente a la siguiente mejor opción.")

st.caption(f"Actualizado: {datetime.now().strftime('%H:%M:%S')}")
