import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Calculadora Cambiaria Vzla", page_icon="💸")

# --- INICIALIZACIÓN DE VALORES BASE ---
# Esto asegura que la app empiece en 304 y 570 y guarde tus cambios manuales
if 't_bcv_manual' not in st.session_state:
    st.session_state.t_bcv_manual = 304.00
if 't_binance_manual' not in st.session_state:
    st.session_state.t_binance_manual = 570.00

st.title("💸 Calculadora de Ahorro")
st.markdown("Configura las tasas manualmente y compara dónde rinde más tu dinero.")

# --- CONFIGURACIÓN EN LA BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración de Tasas")

# Inputs manuales que cargan desde el estado de sesión
t_bcv = st.sidebar.number_input(
    "Tasa BCV (Oficial)", 
    value=st.session_state.t_bcv_manual, 
    format="%.2f",
    key="bcv_input"
)
t_binance = st.sidebar.number_input(
    "Tasa Binance P2P", 
    value=st.session_state.t_binance_manual, 
    format="%.2f",
    key="bin_input"
)

st.sidebar.divider()
st.sidebar.header("🏪 Tasas Personalizadas")
# Tasa de la tienda: por defecto es igual al BCV que pusiste arriba
t_tienda = st.sidebar.number_input("Tasa de la Tienda", value=t_bcv, format="%.2f")
# Tasa de cambista: por defecto es igual a Binance que pusiste arriba
t_cambista = st.sidebar.number_input("Tasa del Cambista", value=t_binance, format="%.2f")

# --- LÓGICA DE CÁLCULO ---
monto_usd = st.number_input("Monto de la compra ($)", min_value=0.1, value=10.0, step=1.0)

# 1. Pago en Efectivo (Monto * 1.03 por el IGTF)
costo_efectivo_usd = monto_usd * 1.03 

# 2. Pago vía Binance (Cambiando dólares para pagar a la tasa de la tienda)
costo_binance_usd = (monto_usd * t_tienda) / t_binance

# 3. Pago vía Cambista
costo_cambista_usd = (monto_usd * t_tienda) / t_cambista

# Determinamos cuál de las opciones en Bolívares es la mejor
mejor_opcion_bs = min(costo_binance_usd, costo_cambista_usd)
metodo_nombre = "Binance" if costo_binance_usd <= costo_cambista_usd else "Cambista"

ahorro = costo_efectivo_usd - mejor_opcion_bs

# --- VISUALIZACIÓN ---
st.header("📊 Comparativa de Costo Real")
col1, col2 = st.columns(2)

with col1:
    st.metric(label="Pagar en Efectivo", value=f"${costo_efectivo_usd:.2f}", help="Incluye el 3% de IGTF")
    st.caption(f"Calculado a tasa tienda: {t_tienda} Bs")

with col2:
    st.metric(label=f"Pagar en Bs (vía {metodo_nombre})", value=f"${mejor_opcion_bs:.2f}", 
              delta=f"-${ahorro:.2f} de ahorro" if ahorro > 0 else f"${ahorro:.2f}")
    st.caption(f"Cambiando a: {max(t_binance, t_cambista)} Bs")

st.divider()

# Mensaje de decisión
if ahorro > 0:
    st.success(f"### ✅ CONVIENE PAGAR EN BOLÍVARES\nTe ahorras un **{((ahorro/costo_efectivo_usd)*100):.1f}%** comparado con usar el efectivo.")
else:
    st.warning("### ⚠️ CONVIENE PAGAR EN EFECTIVO\nLa brecha es demasiado corta o negativa con estas tasas.")

# Tabla de transparencia
st.table({
    "Opción": ["Efectivo (Físico)", "Bolívares (Binance)", "Bolívares (Cambista)"],
    "Tasa de Cambio ($ a Bs)": ["N/A", f"{t_binance} Bs", f"{t_cambista} Bs"],
    "Costo Real ($)": [f"${costo_efectivo_usd:.2f}", f"${costo_binance_usd:.2f}", f"${costo_cambista_usd:.2f}"]
})
