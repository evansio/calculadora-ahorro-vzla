import streamlit as st
import pyDolarVenezuela as pdv

# Configuración inicial
st.set_page_config(page_title="Ahorro Vzla", page_icon="💸")

# --- FUNCIÓN DE EXTRACCIÓN CON MÚLTIPLES INTENTOS ---
@st.cache_data(ttl=30)  # Bajamos a 30 segundos para pruebas
def obtener_tasas_reales():
    tasa_bcv = 0.0
    tasa_bin = 0.0
    
    # Lista de proveedores para intentar uno por uno
    proveedores = [
        pdv.providers.CriptoDolar, # El más estable en la nube
        pdv.providers.Bcv,
        pdv.providers.EnParaleloVzla
    ]
    
    for p in proveedores:
        try:
            monitor = pdv.Monitor(provider=p)
            datos = monitor.get_all_monitors()
            
            for m in datos:
                key = m.lower()
                if ('bcv' in key or 'oficial' in key or 'usd' in key) and tasa_bcv == 0:
                    tasa_bcv = float(datos[m]['price'])
                if ('binance' in key or 'p2p' in key) and tasa_bin == 0:
                    tasa_bin = float(datos[m]['price'])
            
            # Si ya conseguimos ambas, dejamos de buscar en otros proveedores
            if tasa_bcv > 0 and tasa_bin > 0:
                break
        except:
            continue
            
    return tasa_bcv, tasa_bin

# --- INTERFAZ ---
st.title("💸 Calculadora de Ahorro Vzla")

# Intentamos obtener tasas
t_bcv_auto, t_bin_auto = obtener_tasas_reales()

# Si siguen en 0, ponemos valores aproximados actuales para que la app no nazca vacía
if t_bcv_auto == 0: t_bcv_auto = 47.50
if t_bin_auto == 0: t_bin_auto = 57.00

with st.sidebar:
    st.header("⚙️ Ajuste de Tasas")
    
    # El usuario puede ver y corregir los valores si la nube falla
    t_bcv = st.number_input("Tasa Oficial (BCV)", value=t_bcv_auto, format="%.2f")
    t_bin = st.number_input("Tasa Cambio (Binance)", value=t_bin_auto, format="%.2f")
    
    if st.button("🔄 Forzar Actualización"):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.subheader("🏪 Datos de la Tienda")
    t_tienda = st.number_input("Tasa Tienda", value=t_bcv, format="%.2f")
    t_cambista = st.number_input("Tasa Cambista", value=t_bin, format="%.2f")

# --- CÁLCULOS ---
monto = st.number_input("Monto en $", min_value=0.1, value=10.0)

costo_efe = monto * 1.03
costo_bs_bin = (monto * t_tienda) / t_bin
costo_bs_cam = (monto * t_tienda) / t_cambista

mejor_bs = min(costo_bs_bin, costo_bs_cam)
metodo = "Binance" if costo_bs_bin <= costo_bs_cam else "Cambista"
ahorro = costo_efe - mejor_bs

# --- VISUALIZACIÓN TIPO APP ---
st.divider()
c1, c2 = st.columns(2)

with c1:
    st.markdown("### Pagar Efectivo")
    st.title(f"${costo_efe:.2f}")
    st.caption("Incluye 3% IGTF")

with c2:
    st.markdown(f"### Pagar en Bs")
    st.title(f"${mejor_bs:.2f}")
    st.caption(f"Vía {metodo}")

st.divider()

if ahorro > 0:
    st.success(f"### ✅ ¡PAGA EN BOLÍVARES!\nTe ahorras un {((ahorro/costo_efe)*100):.1f}%")
else:
    st.warning("### ⚠️ USA EL EFECTIVO\nNo hay ganancia cambiando a bolívares.")
