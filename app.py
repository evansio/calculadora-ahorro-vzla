import streamlit as st
import pyDolarVenezuela as pdv

# Configuración de la página
st.set_page_config(page_title="Calculadora Ahorro Vzla", page_icon="💸")

st.title("💸 Calculadora de Ahorro Automática")
st.markdown("Tasas actualizadas de **BCV** y **Binance**. Puedes ajustarlas manualmente si lo deseas.")

# --- FUNCIÓN PARA OBTENER TASAS AUTOMÁTICAMENTE ---
@st.cache_data(ttl=600)  # Se actualiza cada 10 minutos para no saturar
def obtener_tasas_en_vivo():
    try:
        # Inicializamos el monitor
        monitor = pdv.Monitor()
        datos = monitor.get_all_monitors()
        
        tasa_bcv = 0.0
        tasa_binance = 0.0
        
        # Buscamos en los datos las llaves que contengan BCV y Binance
        for m in datos:
            key = m.lower()
            if 'bcv' in key and tasa_bcv == 0:
                tasa_bcv = float(datos[m]['price'])
            if 'binance' in key and tasa_binance == 0:
                tasa_binance = float(datos[m]['price'])
        
        return tasa_bcv, tasa_binance
    except Exception as e:
        # Valores de respaldo si la conexión falla (puedes ajustarlos a los de ayer)
        return 47.50, 56.00

# Ejecutamos la función
t_auto_bcv, t_auto_binance = obtener_tasas_en_vivo()

# --- CONFIGURACIÓN EN LA BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración de Tasas")

# Estos inputs se llenan solos con la web, pero permiten edición manual
t_bcv = st.sidebar.number_input("Tasa BCV Oficial", value=t_auto_bcv, format="%.2f")
t_binance = st.sidebar.number_input("Tasa Binance P2P", value=t_auto_binance, format="%.2f")

st.sidebar.divider()
st.sidebar.header("🏪 Tasas Personalizadas")
t_tienda = st.sidebar.number_input("Tasa de la Tienda", value=t_bcv, format="%.2f")
t_cambista = st.sidebar.number_input("Tasa del Cambista", value=t_binance, format="%.2f")

# --- LÓGICA DE CÁLCULO ---
monto_usd = st.number_input("Monto de la compra ($)", min_value=0.1, value=10.0, step=1.0)

# 1. Pago Efectivo: Precio * Tasa Tienda + 3% IGTF
costo_efectivo_usd = monto_usd * 1.03 

# 2. Pago vía Binance/Cambista
# ¿Cuántos $ necesitas vender para cubrir los Bs que pide la tienda?
costo_binance_usd = (monto_usd * t_tienda) / t_binance
costo_cambista_usd = (monto_usd * t_tienda) / t_cambista

# Elegir la mejor opción de Bolívares
mejor_opcion_bs = min(costo_binance_usd, costo_cambista_usd)
nombre_via = "Binance" if costo_binance_usd <= costo_cambista_usd else "Cambista"

ahorro = costo_efectivo_usd - mejor_opcion_bs

# --- RESULTADOS ---
st.header("📊 Resultado del Análisis")
col1, col2 = st.columns(2)

with col1:
    st.metric("Pagar en Efectivo", f"${costo_efectivo_usd:.2f}", help="Incluye 3% IGTF")
    st.caption(f"Tasa tienda: {t_tienda} Bs")

with col2:
    color_delta = "normal" if ahorro > 0 else "inverse"
    st.metric(f"Pagar vía {nombre_via}", f"${mejor_opcion_bs:.2f}", 
              delta=f"-${ahorro:.2f} (Ahorro)" if ahorro > 0 else f"${ahorro:.2f}",
              delta_color=color_delta)
    st.caption(f"Cambiando a: {max(t_binance, t_cambista)} Bs")

st.divider()

if ahorro > 0:
    st.success(f"### ✅ ¡Usa Bolívares!\nTe ahorras un **{((ahorro/costo_efectivo_usd)*100):.1f}%**.")
else:
    st.warning("### ⚠️ Usa Efectivo\nNo hay brecha suficiente para ahorrar cambiando dólares.")

# Tabla de transparencia
st.table({
    "Método": ["Efectivo", "Vía Binance", "Vía Cambista"],
    "Costo Final ($)": [f"${costo_efectivo_usd:.2f}", f"${costo_binance_usd:.2f}", f"${costo_cambista_usd:.2f}"]
})
