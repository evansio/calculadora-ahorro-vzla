import streamlit as st
import pyDolarVenezuela as pdv

# Configuración de la página
st.set_page_config(page_title="Calculadora Cambiaria Vzla", page_icon="💸")

st.title("💸 Calculadora Automática de Ahorro")
st.markdown("Las tasas de **BCV** y **Binance** se actualizan solas. Puedes ajustarlas si es necesario.")

# --- OBTENCIÓN AUTOMÁTICA DE TASAS ---
@st.cache_data(ttl=600)  # Se actualiza cada 10 minutos
def obtener_tasas_en_vivo():
    try:
        monitor = pd.Monitor()
        datos = monitor.get_all_monitors()
        
        tasa_bcv = 0.0
        tasa_binance = 0.0
        
        for m in datos:
            key = m.lower()
            # Buscamos coincidencias para BCV y Binance
            if 'bcv' in key and tasa_bcv == 0:
                tasa_bcv = float(datos[m]['price'])
            if 'binance' in key and tasa_binance == 0:
                tasa_binance = float(datos[m]['price'])
        
        return tasa_bcv, tasa_binance
    except Exception as e:
        # Valores de respaldo si falla la conexión
        return 470.00, 56.00

# Llamada a la función automática
tasa_auto_bcv, tasa_auto_binance = obtener_tasas_en_vivo()

# --- CONFIGURACIÓN EN LA BARRA LATERAL ---
st.sidebar.header("⚙️ Tasas en Tiempo Real")

# Estos inputs toman el valor automático pero te dejan escribir si quieres
t_bcv = st.sidebar.number_input("Tasa BCV (Oficial)", value=tasa_auto_bcv, format="%.2f")
t_binance = st.sidebar.number_input("Tasa Binance P2P", value=tasa_auto_binance, format="%.2f")

st.sidebar.divider()
st.sidebar.header("🏪 Tasas Personalizadas")
# Tasa de la tienda: por defecto es igual al BCV
t_tienda = st.sidebar.number_input("Tasa de la Tienda", value=t_bcv, format="%.2f")
# Tasa de cambista: por defecto es igual a Binance
t_cambista = st.sidebar.number_input("Tasa del Cambista", value=t_binance, format="%.2f")

# --- LÓGICA DE CÁLCULO ---
monto_usd = st.number_input("Monto de la compra ($)", min_value=0.1, value=10.0, step=1.0)

# 1. Pago en Efectivo (Monto * Tasa Tienda + 3% IGTF)
# Calculamos cuánto te cuesta en "dólares reales" pagar con billetes físicos
costo_efectivo_usd = monto_usd * 1.03 

# 2. Pago vía Binance (Usando la Tasa de la Tienda)
# Primero: ¿Cuántos Bs pide la tienda? -> monto_usd * t_tienda
# Segundo: ¿Cuántos $ de tu Binance debes vender para obtener esos Bs?
costo_binance_usd = (monto_usd * t_tienda) / t_binance

# 3. Pago vía Cambista
costo_cambista_usd = (monto_usd * t_tienda) / t_cambista

# Determinamos cuál de las opciones en Bolívares es la mejor
mejor_opcion_bs = min(costo_binance_usd, costo_cambista_usd)
metodo_nombre = "Binance" if costo_binance_usd <= costo_cambista_usd else "Cambista"

ahorro = costo_efectivo_usd - mejor_opcion_bs

# --- RESULTADOS VISUALES ---
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
    st.success(f"### ✅ ¡Cambia tus $ y paga en Bolívares!\nTe ahorras un **{((ahorro/costo_efectivo_usd)*100):.1f}%** comparado con usar el efectivo.")
else:
    st.warning("### ⚠️ Usa tus Dólares en Efectivo\nNo hay suficiente brecha para que valga la pena cambiar.")

# Tabla de transparencia
st.table({
    "Opción": ["Efectivo (Físico)", "Bolívares (Binance)", "Bolívares (Cambista)"],
    "Tasa de Cambio": ["N/A", f"{t_binance} Bs", f"{t_cambista} Bs"],
    "Costo Final ($)": [f"${costo_efectivo_usd:.2f}", f"${costo_binance_usd:.2f}", f"${costo_cambista_usd:.2f}"]
})
