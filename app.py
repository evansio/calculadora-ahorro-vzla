import streamlit as st
import requests
from datetime import datetime

# Configuración mínima
st.set_page_config(
    page_title="¿Cómo Pagar? - Venezuela",
    page_icon="🛒",
    layout="centered"
)

# Logo y título simple
st.markdown("<h1 style='text-align: center;'>🛒 ¿Cómo Pagar?</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #666;'>Te decimos la mejor forma de pagar</h3>", unsafe_allow_html=True)

st.divider()

# --- OBTENER TASA BINANCE (muy simple) ---
@st.cache_data(ttl=300)
def obtener_tasa_binance():
    """Obtiene tasa de Binance P2P"""
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {
            "page": 1, "rows": 1, 
            "asset": "USDT", "tradeType": "BUY", "fiat": "VES"
        }
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and data['data']:
                return float(data['data'][0]['adv']['price'])
    except:
        pass
    return 38.50  # Valor por defecto

# --- CONFIGURACIÓN COMPLETA EN SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Tasas de Hoy")
    
    # Sección 1: Tasas Oficiales
    st.markdown("#### 🏦 Tasas Oficiales")
    
    tasa_bcv = st.number_input(
        "BCV Dólar (Bs/$)",
        value=36.50,
        min_value=1.0,
        step=0.1,
        format="%.2f",
        help="Tasa oficial del Banco Central para Dólar"
    )
    
    tasa_euro = st.number_input(
        "BCV Euro (Bs/€)",
        value=39.50,
        min_value=1.0,
        step=0.1,
        format="%.2f",
        help="Tasa oficial del Banco Central para Euro"
    )
    
    st.divider()
    
    # Sección 2: Tasas Paralelas
    st.markdown("#### 📊 Tasas del Mercado")
    
    # Binance automático
    tasa_binance_auto = obtener_tasa_binance()
    st.metric("Binance P2P", f"{tasa_binance_auto:.2f} Bs")
    
    tasa_binance = st.number_input(
        "Ajustar Binance (Bs/$)",
        value=float(tasa_binance_auto),
        min_value=1.0,
        step=0.1,
        format="%.2f",
        help="Tasa actual del mercado P2P"
    )
    
    tasa_cambista = st.number_input(
        "Tasa Cambista (Bs/$)",
        value=38.00,
        min_value=1.0,
        step=0.1,
        format="%.2f",
        help="Tasa que ofrecen los cambistas locales"
    )
    
    st.divider()
    
    # Información útil
    st.markdown("#### 💡 Información Útil")
    
    # Mostrar diferencias
    dif_binance_bcv = tasa_binance - tasa_bcv
    dif_cambista_bcv = tasa_cambista - tasa_bcv
    dif_euro_dolar = (tasa_euro / tasa_bcv) - 1
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.caption(f"Binance vs BCV: {dif_binance_bcv:+.2f} Bs")
    with col_info2:
        st.caption(f"Cambista vs BCV: {dif_cambista_bcv:+.2f} Bs")
    
    st.caption(f"Euro/Dólar: {(tasa_euro/tasa_bcv):.3f} ({(dif_euro_dolar*100):+.1f}%)")
    
    st.divider()
    
    # Botón de actualización
    if st.button("🔄 Actualizar Binance", type="secondary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- FORMULARIO PRINCIPAL ---
st.markdown("### 📝 ¿Qué producto vas a comprar?")

# Selección de moneda
moneda_tienda = st.radio(
    "¿En qué moneda muestra el precio la tienda?",
    ["🇺🇸 Dólares (USD)", "🇪🇺 Euros (EUR)", "🇻🇪 Bolívares (VES)"],
    horizontal=True
)

col1, col2 = st.columns(2)

if "Bolívares" in moneda_tienda:
    with col1:
        precio_bs = st.number_input(
            "💵 **Precio en Bolívares**",
            min_value=0.01,
            value=3650.0,
            step=100.0,
            format="%.2f",
            help="El precio que ves en la tienda"
        )
    
    with col2:
        precio_usd = st.number_input(
            "💰 **Precio real en Dólares**",
            min_value=0.01,
            value=100.0,
            step=10.0,
            format="%.2f",
            help="¿Cuánto debería costar realmente en USD?"
        )
    
    # Convertir todo a USD para comparación
    precio_usd_comparar = precio_usd

elif "Dólares" in moneda_tienda:
    with col1:
        precio_usd_tienda = st.number_input(
            "💵 **Precio en Dólares**",
            min_value=0.01,
            value=100.0,
            step=10.0,
            format="%.2f",
            help="El precio que ves en la tienda"
        )
    
    with col2:
        precio_usd_real = st.number_input(
            "💰 **Precio real en Dólares**",
            min_value=0.01,
            value=100.0,
            step=10.0,
            format="%.2f",
            help="¿Es un precio justo? (Puede ser igual)"
        )
    
    # Convertir a bolívares según tasa tienda (asumimos BCV para dólares)
    precio_bs = precio_usd_tienda * tasa_bcv
    precio_usd_comparar = precio_usd_real

else:  # Euros
    with col1:
        precio_eur = st.number_input(
            "💶 **Precio en Euros**",
            min_value=0.01,
            value=100.0,
            step=10.0,
            format="%.2f",
            help="El precio que ves en la tienda"
        )
    
    with col2:
        precio_usd_real = st.number_input(
            "💰 **Precio real en Dólares**",
            min_value=0.01,
            value=110.0,
            step=10.0,
            format="%.2f",
            help="¿Cuánto debería costar en USD? (1€ ≈ $1.10)"
        )
    
    # Convertir euros a bolívares según tasa euro
    precio_bs = precio_eur * tasa_euro
    precio_usd_comparar = precio_usd_real

st.divider()

# --- CALCULOS PRINCIPALES ---
if precio_usd_comparar > 0:
    # 1. Calcular tasa que aplica la tienda
    if "Bolívares" in moneda_tienda:
        tasa_tienda = precio_bs / precio_usd_comparar
        moneda_tasa = "Bs/$"
    elif "Dólares" in moneda_tienda:
        tasa_tienda = tasa_bcv  # Asumimos que usan BCV
        moneda_tasa = "Bs/$ (BCV)"
    else:  # Euros
        tasa_tienda = precio_bs / precio_usd_comparar
        moneda_tasa = "Bs/$ (implícita)"
    
    # 2. Calcular costos reales con diferentes opciones
    # Opción A: Pagar en efectivo (dólares) con IGTF
    costo_efectivo_usd = precio_usd_comparar * 1.03
    
    # Opción B: Cambiar dólares a bolívares (Binance)
    costo_binance_usd = precio_bs / tasa_binance
    
    # Opción C: Cambiar dólares a bolívares (Cambista)
    costo_cambista_usd = precio_bs / tasa_cambista
    
    # 3. Encontrar la mejor opción
    opciones = {
        "💵 Pagar en DÓLARES": costo_efectivo_usd,
        "📱 Cambiar vía BINANCE": costo_binance_usd,
        "💱 Cambiar vía CAMBISTA": costo_cambista_usd
    }
    
    mejor_opcion = min(opciones, key=opciones.get)
    mejor_costo = opciones[mejor_opcion]
    
    # Calcular ahorros
    ahorro_vs_efectivo = costo_efectivo_usd - mejor_costo
    porcentaje_ahorro = (ahorro_vs_efectivo / costo_efectivo_usd) * 100
    
    # --- MOSTRAR RESULTADO PRINCIPAL ---
    st.markdown("## 🎯 **RECOMENDACIÓN**")
    
    if "DÓLARES" in mejor_opcion:
        st.error(f"""
        ### ❌ **{mejor_opcion}**
        
        **Costo total:** ${costo_efectivo_usd:.2f} USD
        
        **¿Por qué?**
        - Cambiar a bolívares te saldría más caro
        - La tasa de la tienda no es favorable
        - Paga ${costo_efectivo_usd:.2f} directamente
        """)
    else:
        ahorro_texto = f"${ahorro_vs_efectivo:.2f}" if ahorro_vs_efectivo > 0 else f"-${abs(ahorro_vs_efectivo):.2f}"
        st.success(f"""
        ### ✅ **{mejor_opcion}**
        
        **Costo total:** ${mejor_costo:.2f} USD
        **Ahorras vs efectivo:** {ahorro_texto} ({abs(porcentaje_ahorro):.1f}%)
        
        **Cómo hacerlo:**
        1. Vende ${mejor_costo:.2f} en {'Binance P2P' if 'BINANCE' in mejor_opcion else 'con un cambista'}
        2. Obtén {precio_bs:,.2f} Bs
        3. Paga el producto en bolívares
        4. **¡Ahorraste {ahorro_texto}!**
        """)
    
    st.divider()
    
    # --- COMPARATIVA DE TODAS LAS OPCIONES ---
    st.markdown("### 📊 Comparativa de Opciones")
    
    col_comp1, col_comp2, col_comp3 = st.columns(3)
    
    with col_comp1:
        es_mejor = "💵 Pagar en DÓLARES" == mejor_opcion
        color = "#2e7d32" if es_mejor else "#c62828"
        st.markdown(f"""
        <div style='background-color: #ffebee; padding: 15px; border-radius: 10px; border: 2px solid {color};'>
        <h4 style='color: #c62828;'>💵 En DÓLARES</h4>
        <h3>${costo_efectivo_usd:.2f}</h3>
        <p><small>+3% IGTF incluido</small></p>
        {f"<p style='color: {color};'>🏆 <b>RECOMENDADO</b></p>" if es_mejor else ""}
        </div>
        """, unsafe_allow_html=True)
    
    with col_comp2:
        es_mejor = "📱 Cambiar vía BINANCE" == mejor_opcion
        color = "#2e7d32" if es_mejor else "#666"
        st.markdown(f"""
        <div style='background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 2px solid {color};'>
        <h4 style='color: #2e7d32;'>📱 Con BINANCE</h4>
        <h3>${costo_binance_usd:.2f}</h3>
        <p><small>Tasa: {tasa_binance:.2f} Bs/$</small></p>
        {f"<p style='color: {color};'>🏆 <b>RECOMENDADO</b></p>" if es_mejor else ""}
        </div>
        """, unsafe_allow_html=True)
    
    with col_comp3:
        es_mejor = "💱 Cambiar vía CAMBISTA" == mejor_opcion
        color = "#2e7d32" if es_mejor else "#666"
        st.markdown(f"""
        <div style='background-color: #e3f2fd; padding: 15px; border-radius: 10px; border: 2px solid {color};'>
        <h4 style='color: #1565c0;'>💱 Con CAMBISTA</h4>
        <h3>${costo_cambista_usd:.2f}</h3>
        <p><small>Tasa: {tasa_cambista:.2f} Bs/$</small></p>
        {f"<p style='color: {color};'>🏆 <b>RECOMENDADO</b></p>" if es_mejor else ""}
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # --- INFORMACIÓN ADICIONAL ---
    st.markdown("### ℹ️ Información Detallada")
    
    if "Bolívares" in moneda_tienda:
        st.markdown(f"""
        **📈 La tienda está aplicando:**
        
        **{precio_bs:,.2f} Bs** ÷ **${precio_usd_comparar:.2f} USD** = 
        
        **{tasa_tienda:.2f} {moneda_tasa}**
        """)
    
    # Comparación con tasas del mercado
    st.markdown("#### 📊 Comparación con Tasas de Mercado")
    
    # Crear tabla de comparación - CORREGIDO
    st.markdown("| Tipo de Tasa | Valor (Bs/$) | Diferencia |")
    st.markdown("|-------------|-------------|------------|")
    
    # Fila 1: Tasa Tienda
    if "Bolívares" in moneda_tienda:
        st.markdown(f"| Tasa Tienda | {tasa_tienda:.2f} | — |")
    else:
        st.markdown("| Tasa Tienda | N/A | — |")
    
    # Fila 2: BCV Oficial
    st.markdown(f"| BCV Oficial | {tasa_bcv:.2f} | — |")
    
    # Filas 3 y 4: Solo mostrar diferencias si hay tasa tienda
    if "Bolívares" in moneda_tienda:
        # Binance P2P
        diff_binance = tasa_binance - tasa_tienda
        color_binance = "🟢" if diff_binance > 0 else "🔴" if diff_binance < 0 else "⚪"
        st.markdown(f"| Binance P2P | {tasa_binance:.2f} | {diff_binance:+.2f} Bs {color_binance} |")
        
        # Tasa Cambista
        diff_cambista = tasa_cambista - tasa_tienda
        color_cambista = "🟢" if diff_cambista > 0 else "🔴" if diff_cambista < 0 else "⚪"
        st.markdown(f"| Tasa Cambista | {tasa_cambista:.2f} | {diff_cambista:+.2f} Bs {color_cambista} |")
    else:
        st.markdown(f"| Binance P2P | {tasa_binance:.2f} | — |")
        st.markdown(f"| Tasa Cambista | {tasa_cambista:.2f} | — |")
    
    st.markdown("")
    st.markdown("*🟢 Mejor que la tienda | 🔴 Peor que la tienda | ⚪ Igual*")
    
    # Explicación de las diferencias
    if "Bolívares" in moneda_tienda:
        if tasa_tienda < tasa_binance:
            st.success(f"✅ **La tasa de la tienda ({tasa_tienda:.2f} Bs/$) es MEJOR que Binance ({tasa_binance:.2f} Bs/$)**")
            st.caption("Esto significa que la tienda está usando una tasa más favorable para ti.")
        elif tasa_tienda > tasa_binance:
            st.warning(f"⚠️ **La tasa de la tienda ({tasa_tienda:.2f} Bs/$) es PEOR que Binance ({tasa_binance:.2f} Bs/$)**")
            st.caption("La tienda está cobrando una tasa más alta que el mercado.")
        else:
            st.info(f"ℹ️ **La tasa de la tienda ({tasa_tienda:.2f} Bs/$) es IGUAL que Binance**")
    
    st.divider()
    
    # --- RESUMEN FINAL ---
    st.markdown("### 📋 Resumen Final")
    
    resumen_html = f"""
    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px;'>
    <h4>🏷️ Detalles del Producto</h4>
    <p><strong>Moneda tienda:</strong> {moneda_tienda.split(' ')[-1]}</p>
    <p><strong>Precio tienda:</strong> {precio_bs:,.2f} Bs / ${precio_usd_comparar:.2f} USD</p>
    """
    
    if "Bolívares" in moneda_tienda:
        resumen_html += f"""<p><strong>Tasa aplicada:</strong> {tasa_tienda:.2f} Bs/$</p>"""
    
    resumen_html += f"""
    <hr>
    <h4>🎯 Mejor Opción</h4>
    <p><strong>{mejor_opcion}</strong></p>
    <p><strong>Costo real:</strong> ${mejor_costo:.2f} USD</p>
    <p><strong>Ahorro vs efectivo:</strong> ${ahorro_vs_efectivo:+.2f} USD</p>
    </div>
    """
    
    st.markdown(resumen_html, unsafe_allow_html=True)

else:
    st.info("👆 **Por favor, ingresa el precio real en dólares del producto**")

# --- FOOTER ---
st.divider()
st.markdown(f"""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
<p>🔄 Binance: {tasa_binance:.2f} Bs/$ | 🏦 BCV: {tasa_bcv:.2f} Bs/$ | 🇪🇺 Euro: {tasa_euro:.2f} Bs/€</p>
<p><em>Actualizado: {datetime.now().strftime('%H:%M')} • Calcula siempre antes de pagar</em></p>
</div>
""", unsafe_allow_html=True)
