import streamlit as st
import pyDolarVenezuela as pdv

# 1. Configuración inicial
st.set_page_config(page_title="Ahorro Vzla", page_icon="💸")

# 2. Inicializar la memoria (Session State)
# Esto evita que los valores se reseteen al escribir
if 'tasa_bcv' not in st.session_state:
    st.session_state.tasa_bcv = 0.0
if 'tasa_binance' not in st.session_state:
    st.session_state.tasa_binance = 0.0

# 3. Función para obtener tasas (Solo se ejecuta si la memoria está vacía o pides actualizar)
def obtener_datos():
    try:
        monitor = pdv.Monitor(provider=pdv.providers.CriptoDolar)
        datos = monitor.get_all_monitors()
        bcv, binance = 0.0, 0.0
        for m in datos:
            key = m.lower()
            if ('bcv' in key or 'usd' in key) and bcv == 0:
                bcv = float(datos[m]['price'])
            if ('binance' in key or 'p2p' in key) and binance == 0:
                binance = float(datos[m]['price'])
        return bcv, binance
    except:
        return 304.6796, 57.50

# Cargar datos automáticos solo la primera vez
if st.session_state.tasa_bcv == 0:
    bcv_auto, bin_auto = obtener_datos()
    st.session_state.tasa_bcv = bcv_auto
    st.session_state.tasa_binance = bin_auto

# --- INTERFAZ ---
st.title("💸 Calculadora Ahorro Vzla")

with st.sidebar:
    st.header("⚙️ Ajuste de Tasas")
    
    # Usamos los valores de la memoria (session_state)
    t_bcv = st.number_input("Tasa BCV", value=st.session_state.tasa_bcv, format="%.2f")
    t_bin = st.number_input("Tasa Binance", value=st.session_state.tasa_binance, format="%.2f")
    
    # Botón para forzar actualización manual
    if st.button("🔄 Actualizar desde Internet"):
        bcv_up, bin_up = obtener_datos()
        st.session_state.tasa_bcv = bcv_up
        st.session_state.tasa_binance = bin_up
        st.rerun()

    st.divider()
    st.subheader("🏪 Datos de Tienda")
    # Estos dependen de lo que pongas arriba
    t_tienda = st.number_input("Tasa Tienda", value=t_bcv, format="%.2f")
    t_cambista = st.number_input("Tasa Cambista", value=t_bin, format="%.2f")

# --- CÁLCULOS ---
monto = st.number_input("Monto de compra ($)", min_value=0.1, value=10.0)

costo_efe = monto * 1.03
costo_bs_bin = (monto * t_tienda) / t_bin
costo_bs_cam = (monto * t_tienda) / t_cambista

mejor_bs = min(costo_bs_bin, costo_bs_cam)
metodo = "Binance" if costo_bs_bin <= costo_bs_cam else "Cambista"
ahorro = costo_efe - mejor_bs

# --- VISUALIZACIÓN ---
st.divider()
c1, c2 = st.columns(2)

with c1:
    st.metric("Efectivo (+3%)", f"${costo_efe:.2f}")
with c2:
    st.metric(f"Pago en Bs ({metodo})", f"${mejor_bs:.2f}", 
              delta=f"${ahorro:.2f}" if ahorro > 0 else f"${ahorro:.2f}")

if ahorro > 0:
    st.success(f"### ✅ ¡CONVIENE PAGAR EN BS!\nAhorro: {((ahorro/costo_efe)*100):.1f}%")
else:
    st.warning("### ⚠️ USA EFECTIVO")


