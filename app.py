import streamlit as st
import pyDolarVenezuela as pdv

# Configuración visual
st.set_page_config(page_title="Ahorro Vzla", page_icon="💸")

st.title("💸 Calculadora de Ahorro Vzla")
st.markdown("Comparación inteligente de tasas en tiempo real.")

# --- LÓGICA DE EXTRACCIÓN ROBUSTA ---
@st.cache_data(ttl=60) # Actualización automática cada 60 segundos
def obtener_tasas_dinamicas():
    tasa_bcv = 0.0
    tasa_binance = 0.0
    
    try:
        # Intento 1: Usar el monitor general (más rápido)
        monitor = pdv.Monitor()
        datos = monitor.get_all_monitors()
        
        for m in datos:
            key = m.lower()
            if 'bcv' in key and tasa_bcv == 0:
                tasa_bcv = float(datos[m]['price'])
            if 'binance' in key and tasa_binance == 0:
                tasa_binance = float(datos[m]['price'])
        
        # Intento 2: Si el 1 falló, buscar por proveedores específicos
        if tasa_bcv == 0:
            bcv_prov = pdv.Monitor(provider=pdv.providers.Bcv)
            tasa_bcv = float(bcv_prov.get_specific_monitor(monitor_code='usd')['price'])
            
        if tasa_binance == 0:
            binance_prov = pdv.Monitor(provider=pdv.providers.EnParaleloVzla)
            tasa_binance = float(binance_prov.get_specific_monitor(monitor_code='binance')['price'])
            
    except Exception as e:
        # Si todo falla, mostrar error técnico para saber qué pasó
        st.sidebar.warning(f"Nota: Usando valores manuales (Error: {e})")
        
    # Valores de último recurso si la red falla totalmente
    if tasa_bcv == 0: tasa_bcv = 47.60
    if tasa_binance == 0: tasa_binance = 56.50
    
    return tasa_bcv, tasa_binance

# Botón para forzar actualización
if st.sidebar.button("🔄 Actualizar Tasas"):
    st.cache_data.clear()
    st.rerun()

t_auto_bcv, t_auto_binance = obtener_tasas_dinamicas()

# --- INTERFAZ LATERAL ---
st.sidebar.header("⚙️ Tasas Actuales")
t_bcv = st.sidebar.number_input("BCV (Oficial)", value=t_auto_bcv, format="%.2f")
t_binance = st.sidebar.number_input("Binance P2P", value=t_auto_binance, format="%.2f")

st.sidebar.divider()
st.sidebar.subheader("🏪 Configuración de Tienda")
t_tienda = st.sidebar.number_input("Tasa que cobra la tienda", value=t_bcv, format="%.2f")
t_cambista = st.sidebar.number_input("Tasa de tu cambista ($ físico)", value=t_binance, format="%.2f")

# --- CÁLCULOS ---
monto_usd = st.number_input("Monto de la compra ($)", min_value=0.1, value=10.0, step=1.0)

# Escenario A: Efectivo (Incluye 3% IGTF sobre el precio convertido a la tasa de la tienda)
costo_efectivo_real = monto_usd * 1.03

# Escenario B: Pagar en Bolívares (Cambiando dólares en Binance o con cambista)
costo_via_binance = (monto_usd * t_tienda) / t_binance
costo_via_cambista = (monto_usd * t_tienda) / t_cambista

# Elegir la mejor ruta de bolívares
mejor_costo_bs = min(costo_via_binance, costo_via_cambista)
metodo_nombre = "Binance" if costo_via_binance <= costo_via_cambista else "Cambista"

ahorro = costo_efectivo_real - mejor_costo_bs

# --- VISUALIZACIÓN ---
st.subheader("📊 Comparación de Costo Real")
col1, col2 = st.columns(2)

with col1:
    st.metric("Pago en Efectivo", f"${costo_efectivo_real:.2f}", help="Incluye 3% IGTF")
    st.caption(f"A tasa tienda: {t_tienda}")

with col2:
    color_delta = "normal" if ahorro > 0 else "inverse"
    st.metric(f"Pago en Bs (vía {metodo_nombre})", f"${mejor_costo_bs:.2f}", 
              delta=f"-${ahorro:.2f} Ahorro" if ahorro > 0 else f"${ahorro:.2f}",
              delta_color=color_delta)
    st.caption(f"Cambiando a: {max(t_binance, t_cambista)}")

st.divider()

if ahorro > 0:
    st.success(f"### ✅ CONVIENE PAGAR EN BOLÍVARES\nTe ahorras un **{((ahorro/costo_efectivo_real)*100):.1f}%** de tu dinero.")
else:
    st.warning("### ⚠️ CONVIENE PAGAR EN EFECTIVO\nLa brecha es muy corta o la tienda tiene una tasa muy alta.")

# Tabla detallada
with st.expander("Ver detalles de la comparación"):
    st.table({
        "Método": ["Efectivo (Físico)", "Bolívares (vía Binance)", "Bolívares (vía Cambista)"],
        "Tasa de cambio aplicada": ["N/A", f"{t_binance} Bs", f"{t_cambista} Bs"],
        "Costo Final en $": [f"${costo_efectivo_real:.2f}", f"${costo_via_binance:.2f}", f"${costo_via_cambista:.2f}"]
    })
