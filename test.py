import streamlit as st
import pandas as pd
import sys
import os
import importlib.util
import importlib
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configurar el path para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'DB'))
sys.path.insert(0, os.path.join(current_dir, 'Calculations'))
sys.path.insert(0, os.path.join(current_dir, 'ML'))
sys.path.insert(0, os.path.join(current_dir, 'Routines'))

import_errors = {}

def safe_import(module_path, class_name, force_reload=False):
    try:
        if force_reload and module_path in sys.modules:
            importlib.reload(sys.modules[module_path])
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        return cls, True, None
    except Exception as e:
        import_errors[module_path] = str(e)
        return None, False, str(e)

Rutina_cls, is_rutina_ok, err_rutina = safe_import('rutinas', 'Rutina')
Calculos_cls, is_calculos_ok, err_calculos = safe_import('calculos', 'Calculos')

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="AstroQuipu - Análisis Astronómico",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONALIZADO (Estilo Dashboard Espacial) ---
st.markdown("""
<style>
    /* Variables de color */
    :root {
        --space-dark: #0a0e17;
        --space-blue: #1a2b47;
        --accent: #00e5ff;
        --text: #e0f7fa;
        --border: rgba(0, 229, 255, 0.2);
        --card-bg: rgba(26, 43, 71, 0.6);
        --hover-bg: rgba(0, 229, 255, 0.1);
    }
    
    /* Fondo principal */
    .stApp {
        background: radial-gradient(circle at center, #000 0%, #001017 70%, #002024 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(10, 14, 23, 0.95) !important;
        border-right: 1px solid rgba(0, 229, 255, 0.2);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0f7fa;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #e0f7fa !important;
        font-family: 'Outfit', sans-serif;
    }
    
    h1 {
        background: linear-gradient(90deg, #00e5ff, #0077ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Texto general */
    .stMarkdown, p, span, label {
        color: #e0f7fa !important;
    }
    
    /* Botones */
    .stButton > button {
        background: transparent !important;
        border: 1px solid #00e5ff !important;
        color: #00e5ff !important;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: rgba(0, 229, 255, 0.2) !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
        transform: translateY(-2px);
    }
    
    /* Selectbox y inputs */
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        background: rgba(10, 14, 23, 0.8) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        color: #e0f7fa !important;
        border-radius: 6px;
    }
    
    .stSelectbox > div > div:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #00e5ff !important;
        box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.2);
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: transparent;
    }
    
    .stRadio > div > label {
        color: #e0f7fa !important;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        transition: all 0.3s ease;
        border-left: 3px solid transparent;
    }
    
    .stRadio > div > label:hover {
        background: rgba(0, 229, 255, 0.1);
        border-left-color: #00e5ff;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 1px solid rgba(0, 229, 255, 0.2);
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #e0f7fa;
        border: none;
        padding: 1rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(0, 229, 255, 0.1);
        color: #00e5ff !important;
        border-bottom: 2px solid #00e5ff;
    }
    
    /* Cards / Expanders */
    .stExpander {
        background: rgba(26, 43, 71, 0.6);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 12px;
    }
    
    /* DataFrames */
    .stDataFrame {
        background: rgba(10, 14, 23, 0.8);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 8px;
    }
    
    [data-testid="stDataFrame"] > div {
        background: rgba(10, 14, 23, 0.8) !important;
    }
    
    /* Info/Warning/Error boxes */
    .stAlert {
        background: rgba(26, 43, 71, 0.8);
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 8px;
        color: #e0f7fa;
    }
    
    [data-testid="stAlert"] {
        background: rgba(0, 229, 255, 0.1) !important;
        border-left: 4px solid #00e5ff;
    }
    
    /* Success messages */
    .element-container .stSuccess {
        background: rgba(0, 255, 100, 0.1);
        border-left: 4px solid #00ff64;
    }
    
    /* Spinners */
    .stSpinner > div {
        border-top-color: #00e5ff !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(26, 43, 71, 0.4);
        border: 2px dashed rgba(0, 229, 255, 0.3);
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(26, 43, 71, 0.6);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 12px;
        padding: 1rem;
    }
    
    [data-testid="stMetricValue"] {
        color: #00e5ff !important;
        font-size: 2rem !important;
    }
    
    /* Plotly charts dark theme */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Sidebar title styling */
    .sidebar-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #00e5ff;
        padding: 1rem 0;
        border-bottom: 1px solid rgba(0, 229, 255, 0.2);
        margin-bottom: 1rem;
    }
    
    /* Custom card class */
    .custom-card {
        background: rgba(26, 43, 71, 0.6);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Status indicator */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active { background: #00ff64; box-shadow: 0 0 8px #00ff64; }
    .status-inactive { background: #ff4444; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(10, 14, 23, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 229, 255, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 229, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "🏠 Inicio"
if 'datos_actuales' not in st.session_state:
    st.session_state.datos_actuales = None
if 'fuente_actual' not in st.session_state:
    st.session_state.fuente_actual = None
if 'metadatos' not in st.session_state:
    st.session_state.metadatos = {}
if 'rutina_instance' not in st.session_state:
    if is_rutina_ok:
        st.session_state.rutina_instance = Rutina_cls()

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; padding: 1rem 0;">
            <span style="font-size: 1.8rem; color: #00e5ff;">◉</span>
            <span style="font-size: 1.4rem; font-weight: 600; color: #e0f7fa;">AstroQuipu</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="font-size: 0.9rem; color: rgba(224, 247, 250, 0.7); margin-bottom: 1.5rem;">
            Sistema de Análisis Astronómico
        </div>
    """, unsafe_allow_html=True)
    
    # Botón recargar
    if st.button("🔄 Recargar Módulos", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        modules_to_reload = ['DB.entrada', 'DB.BaseDatos', 'rutinas', 'calculos']
        for module_name in modules_to_reload:
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
        Rutina_cls, is_rutina_ok, _ = safe_import('rutinas', 'Rutina', force_reload=True)
        if is_rutina_ok:
            st.session_state.rutina_instance = Rutina_cls()
        st.session_state.pagina = "🏠 Inicio"
        st.rerun()
    
    st.markdown("<hr style='border-color: rgba(0, 229, 255, 0.2); margin: 1rem 0;'>", unsafe_allow_html=True)
    
    # Navegación
    pagina = st.radio(
        "Navegación",
        ["🏠 Inicio", "📂 Cargar Datos", "🔭 Cálculos", "🤖 Machine Learning", "📃 Reporte"],
        key="nav_radio",
        label_visibility="collapsed"
    )
    st.session_state.pagina = pagina
    
    st.markdown("<hr style='border-color: rgba(0, 229, 255, 0.2); margin: 1rem 0;'>", unsafe_allow_html=True)
    
    # Estado de datos
    st.markdown("### 📊 Estado de Datos")
    if st.session_state.datos_actuales is not None:
        st.markdown(f"""
            <div style="background: rgba(0, 255, 100, 0.1); border: 1px solid rgba(0, 255, 100, 0.3); 
                        border-radius: 8px; padding: 1rem; margin-top: 0.5rem;">
                <div style="color: #00ff64; font-weight: 600; margin-bottom: 0.5rem;">
                    <span class="status-indicator status-active"></span> Datos Cargados
                </div>
                <div style="font-size: 0.85rem; color: #e0f7fa;">
                    <strong>Fuente:</strong> {st.session_state.fuente_actual}<br>
                    <strong>Registros:</strong> {len(st.session_state.datos_actuales):,}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="background: rgba(255, 68, 68, 0.1); border: 1px solid rgba(255, 68, 68, 0.3); 
                        border-radius: 8px; padding: 1rem; margin-top: 0.5rem;">
                <div style="color: #ff6b6b; font-weight: 600;">
                    <span class="status-indicator status-inactive"></span> Sin datos cargados
                </div>
                <div style="font-size: 0.85rem; color: rgba(224, 247, 250, 0.7); margin-top: 0.5rem;">
                    Selecciona una fuente de datos para comenzar
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- CONTENIDO PRINCIPAL ---

# === PÁGINA DE INICIO ===
if pagina == "🏠 Inicio":
    st.markdown("""
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">🌌 AstroQuipu</h1>
        <p style="font-size: 1.2rem; color: rgba(224, 247, 250, 0.8); margin-bottom: 2rem;">
            Sistema de Análisis de Datos Astronómicos
        </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="custom-card">
                <h3 style="color: #00e5ff; margin-bottom: 1rem;">📂 Cargar Datos</h3>
                <p style="font-size: 0.9rem;">Conecta con SDSS, DESI, NASA ESI, NEO o carga archivos locales.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="custom-card">
                <h3 style="color: #00e5ff; margin-bottom: 1rem;">🔭 Análisis</h3>
                <p style="font-size: 0.9rem;">Cálculos cosmológicos, orbitales y visualizaciones 3D interactivas.</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="custom-card">
                <h3 style="color: #00e5ff; margin-bottom: 1rem;">🤖 Machine Learning</h3>
                <p style="font-size: 0.9rem;">Clustering, clasificación y análisis predictivo de datos astronómicos.</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.info("💡 Utiliza el menú lateral para navegar entre las diferentes secciones del sistema.")

# === PÁGINA CARGAR DATOS ===
elif pagina == "📂 Cargar Datos":
    st.markdown("<h1>📂 Cargar Datos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: rgba(224, 247, 250, 0.8);'>Selecciona la fuente de datos astronómicos para iniciar el análisis.</p>", unsafe_allow_html=True)
    
    fuentes_opciones = {
        1: "📁 Archivos Locales (CSV/DAT)",
        2: "🌀 SDSS - Galaxias y espectros",
        3: "🔭 DESI - Objetos del cosmos profundo",
        4: "🪐 NASA ESI - Exoplanetas",
        5: "☄️ NEO - Asteroides y Cometas"
    }
    
    opcion_seleccionada = st.selectbox(
        "Selecciona la fuente de datos:",
        options=list(fuentes_opciones.keys()),
        format_func=lambda x: fuentes_opciones[x],
        key="selector_fuente"
    )
    
    st.markdown(f"""
        <div style="background: rgba(0, 229, 255, 0.1); border-left: 4px solid #00e5ff; 
                    padding: 1rem; border-radius: 0 8px 8px 0; margin: 1rem 0;">
            <strong style="color: #00e5ff;">Fuente seleccionada:</strong> 
            <span style="color: #e0f7fa;">{fuentes_opciones[opcion_seleccionada].split(' - ')[0]}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Archivos Locales
    if opcion_seleccionada == 1:
        st.markdown("### 📁 Subir Archivo Local")
        uploaded_file = st.file_uploader("Arrastra o selecciona un archivo CSV o DAT", type=["csv", "dat"])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state.datos_actuales = df
                st.session_state.fuente_actual = f"Local: {uploaded_file.name}"
                st.success(f"✅ Archivo {uploaded_file.name} cargado correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al leer el archivo: {e}")

    # SDSS / DESI
    elif opcion_seleccionada in [2, 3]:
        nombre_corto = "SDSS" if opcion_seleccionada == 2 else "DESI"
        st.markdown(f"### 🌐 Consulta Remota: {nombre_corto}")
        
        col_ra, col_dec = st.columns(2)
        with col_ra:
            ra = st.number_input("Ascensión Recta (RA, grados)", value=180.0, key="ra")
        with col_dec:
            dec = st.number_input("Declinación (DEC, grados)", value=0.0, key="dec")

        col_zmin, col_zmax, col_rad = st.columns(3)
        with col_zmin:
            z_min = st.number_input("Redshift Mínimo", value=0.05, key="z_min")
        with col_zmax:
            z_max = st.number_input("Redshift Máximo", value=0.3, key="z_max")
        with col_rad:
            radius = st.number_input("Radio de Búsqueda (°)", value=1.0, key="radius")

        if st.button(f"🔍 Consultar {nombre_corto}", key="btn_sdss_desi", use_container_width=True):
            with st.spinner(f"Contactando a {nombre_corto}..."):
                try:
                    resultado = st.session_state.rutina_instance.base_datos.conectar(
                        ra=ra, dec=dec, z_min=z_min, z_max=z_max, radius=radius, source=nombre_corto
                    )
                    if resultado is not None:
                        df = resultado.to_pandas() if hasattr(resultado, 'to_pandas') else resultado
                        st.session_state.datos_actuales = df
                        st.session_state.fuente_actual = nombre_corto
                        st.session_state.metadatos['consulta'] = {'ra': ra, 'dec': dec, 'z_min': z_min, 'z_max': z_max, 'radius': radius}
                        st.session_state.rutina_instance.base_datos.guardardatos(resultado, nombre_corto)
                        st.success(f"✅ ¡Éxito! Se cargaron {len(df)} registros de {nombre_corto}.")
                        st.rerun()
                    else:
                        st.error("❌ No se obtuvieron resultados o la consulta falló.")
                except Exception as e:
                    st.error(f"❌ Error al consultar {nombre_corto}: {e}")

    # NASA ESI
    elif opcion_seleccionada == 4:
        st.markdown("### 🪐 NASA ESI - Exoplanetas")
        st.markdown("Consulta la base de datos de exoplanetas de la NASA (datos recientes con radio conocido).")
        
        if st.button("🔍 Consultar NASA ESI", key="btn_nasa_esi", use_container_width=True):
            with st.spinner("Contactando a NASA Exoplanet Archive..."):
                try:
                    resultado = st.session_state.rutina_instance.base_datos.conectar(source="NASA ESI")
                    if resultado is not None:
                        df = resultado.to_pandas() if hasattr(resultado, 'to_pandas') else resultado
                        st.session_state.datos_actuales = df
                        st.session_state.fuente_actual = "NASA ESI"
                        st.success(f"✅ ¡Éxito! Se cargaron {len(df)} exoplanetas.")
                        st.rerun()
                    else:
                        st.error("❌ No se obtuvieron resultados.")
                except Exception as e:
                    st.error(f"❌ Error al consultar NASA ESI: {e}")

    # NEO
    elif opcion_seleccionada == 5:
        st.markdown("### ☄️ NEO - Near-Earth Objects")
        
        opciones_neo = [
            "Ceres", "Pallas", "Vesta", "Eros", "Apollo",
            "Toutatis", "Phaethon", "Geographos", "Itokawa",
            "Bennu", "Apophis", "Ryugu", "Mathilde",
            "Didymos", "2013 VY4"
        ]
        
        seleccion_neo = st.selectbox("Selecciona el objeto a consultar:", opciones_neo, key="selector_neo")
        
        if st.button("🔍 Consultar JPL Horizons", key="btn_neo", use_container_width=True):
            with st.spinner(f"Conectando con JPL (NASA) para buscar {seleccion_neo}..."):
                try:
                    resultado = st.session_state.rutina_instance.base_datos.conectar(source="NEO", object_name=seleccion_neo)
                    if resultado is not None:
                        df = resultado.to_pandas() if hasattr(resultado, 'to_pandas') else resultado
                        st.session_state.datos_actuales = df
                        st.session_state.fuente_actual = f"NEO - {seleccion_neo}"
                        st.success(f"✅ Datos orbitales de {seleccion_neo} descargados correctamente.")
                        st.rerun()
                    else:
                        st.error("❌ No se obtuvieron resultados.")
                except Exception as e:
                    st.error(f"❌ Error en la consulta: {str(e)}")

# === PÁGINA DE CÁLCULOS ===
elif pagina == "🔭 Cálculos":
    if st.session_state.datos_actuales is None:
        st.warning("⚠️ No hay datos cargados. Por favor, carga datos primero desde la sección 'Cargar Datos'.")
    elif not is_calculos_ok:
        st.error(f"❌ Error importando Calculos: {err_calculos}")
    else:
        df = st.session_state.datos_actuales.copy()
        source = st.session_state.fuente_actual
        calc_instance = Calculos_cls()
        
        st.markdown(f"<h1>🔭 Laboratorio de Análisis</h1>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="background: rgba(0, 229, 255, 0.1); border-left: 4px solid #00e5ff; 
                        padding: 1rem; border-radius: 0 8px 8px 0; margin-bottom: 1.5rem;">
                <strong style="color: #00e5ff;">Fuente activa:</strong> 
                <span style="color: #e0f7fa;">{source}</span>
                <span style="margin-left: 1rem; color: rgba(224, 247, 250, 0.7);">({len(df):,} registros)</span>
            </div>
        """, unsafe_allow_html=True)
        
        # SDSS
        if "SDSS" in source:
            tab1, tab2, tab3 = st.tabs(["📊 Estadísticas", "🌌 Mapa 3D", "📈 Cálculos"])
            
            with tab1:
                st.markdown("### Distribución de Redshift (z)")
                if 'z' in df.columns:
                    fig_hist = px.histogram(df, x="z", nbins=50, title="Histograma de Redshift",
                                          color_discrete_sequence=['#00e5ff'])
                    fig_hist.update_layout(
                        template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#e0f7fa')
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                    z_peak = df['z'].mode()[0] if not df['z'].mode().empty else 0
                    st.info(f"💡 El pico de detección está en z ≈ {z_peak:.3f}. Esto podría indicar un cúmulo de galaxias.")

            with tab2:
                st.markdown("### 🗺️ La Telaraña Cósmica (3D)")
                if st.button("🚀 Generar Mapa 3D", key="btn_mapa_3d", use_container_width=True):
                    with st.spinner("Triangulando posiciones en el universo..."):
                        df_3d = calc_instance.generar_coordenadas_cartesianas(df)
                        if df_3d is not None:
                            fig_3d = px.scatter_3d(df_3d, x='x_coord', y='y_coord', z='z_coord',
                                                 color='z', opacity=0.7,
                                                 title="Mapa 3D del Universo Observable (Mpc)",
                                                 color_continuous_scale='Viridis')
                            fig_3d.update_traces(marker=dict(size=3))
                            fig_3d.update_layout(template="plotly_dark", scene=dict(aspectmode='data'),
                                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                            st.plotly_chart(fig_3d, use_container_width=True)
                            st.success("✅ Mapa generado. Usa el mouse para rotar y hacer zoom.")
                        else:
                            st.error("Faltan columnas RA/DEC/Z para generar el mapa.")

            with tab3:
                st.markdown("### Aplicar Cálculos Numéricos")
                if st.button("📐 Calcular Distancias Hubble", use_container_width=True):
                    new_df, report = calc_instance.aplicar_cosmologia(df)
                    st.session_state.datos_actuales = new_df
                    st.session_state.metadatos['ultimo_reporte'] = report
                    st.success("✅ Cálculos aplicados correctamente.")
                    st.dataframe(new_df[['z', 'Distancia_Hubble_Mpc', 'Velocidad_Recesion_km_s']].head(10))

        # NEO
        elif "NEO" in source:
            tab1, tab2 = st.tabs(["🛸 Simulador Orbital", "📋 Parámetros"])
            
            with tab1:
                st.markdown("### Simulación Orbital Futura")
                col_sim1, col_sim2 = st.columns([1, 2])
                with col_sim1:
                    dias_futuro = st.number_input("Días a simular:", min_value=1, max_value=36500, value=365, step=30)
                    run_sim = st.button("🚀 Simular Trayectoria", use_container_width=True)
                
                with col_sim2:
                    if run_sim:
                        datos_sim = calc_instance.simular_orbita_futura(df, dias=dias_futuro)
                        if "error" not in datos_sim:
                            fig_orb = go.Figure()
                            fig_orb.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', 
                                             marker=dict(size=10, color='yellow'), name='Sol'))
                            fig_orb.add_trace(go.Scatter3d(x=datos_sim['trayectoria_x'], y=datos_sim['trayectoria_y'], 
                                             z=datos_sim['trayectoria_z'], mode='lines', 
                                             line=dict(color='#00e5ff', width=2), name='Órbita'))
                            fig_orb.add_trace(go.Scatter3d(x=[datos_sim['futuro_x']], y=[datos_sim['futuro_y']], 
                                             z=[datos_sim['futuro_z']], mode='markers+text', 
                                             marker=dict(size=6, color='#ff4444'), 
                                             text=[f"{datos_sim['objeto']} (+{dias_futuro}d)"], 
                                             textposition="top center", name='Futuro'))
                            fig_orb.update_layout(title=f"Simulación de {datos_sim['objeto']}",
                                                scene=dict(aspectmode='data', xaxis_title='X (AU)', 
                                                          yaxis_title='Y (AU)', zaxis_title='Z (AU)'),
                                                template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
                                                margin=dict(l=0, r=0, b=0, t=40))
                            st.plotly_chart(fig_orb, use_container_width=True)
                            st.info(f"📍 Coordenadas predichas (AU): X={datos_sim['futuro_x']:.3f}, Y={datos_sim['futuro_y']:.3f}, Z={datos_sim['futuro_z']:.3f}")
                        else:
                            st.error(f"No se pudo simular: {datos_sim['error']}")
            
            with tab2:
                st.markdown("### Datos Orbitales Cargados")
                st.dataframe(df, use_container_width=True)
                if st.button("📐 Calcular Velocidades Medias", use_container_width=True):
                    new_df, report = calc_instance.aplicar_orbitales(df)
                    st.session_state.datos_actuales = new_df
                    st.session_state.metadatos['ultimo_reporte'] = report
                    st.success("✅ Cálculos aplicados.")
                    st.rerun()

        # NASA ESI - Exoplanetas
        elif "NASA ESI" in source:
            if 'Clase_Planeta' not in df.columns:
                df, _ = calc_instance.aplicar_exoplanetas(df)
                st.session_state.datos_actuales = df

            st.info(f"🪐 Analizando {len(df)} exoplanetas confirmados.")
            tab1, tab2, tab3 = st.tabs(["🔵 Masa vs Radio", "☀️ Zona Habitable", "📅 Descubrimientos"])
            
            with tab1:
                st.markdown("### Clasificación por Composición")
                if 'pl_bmasse' in df.columns and 'pl_rade' in df.columns:
                    fig_comp = px.scatter(df, x="pl_bmasse", y="pl_rade", color="Clase_Planeta",
                                        hover_data=['pl_name', 'pl_orbper'], log_x=True, log_y=True,
                                        labels={'pl_bmasse': 'Masa (Masas Terrestres)', 'pl_rade': 'Radio (Radios Terrestres)'},
                                        title="Relación Masa-Radio de Exoplanetas")
                    fig_comp.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_comp, use_container_width=True)

            with tab2:
                st.markdown("### La Zona de 'Ricitos de Oro'")
                if 'distancia_estimada_AU' in df.columns and 'st_teff' in df.columns:
                    df_viz = df[df['distancia_estimada_AU'] < 5].copy()
                    fig_hab = px.scatter(df_viz, x="distancia_estimada_AU", y="st_teff", color="Zona_Termica",
                                       size="pl_rade", hover_data=['pl_name'],
                                       color_discrete_map={'Zona Habitable (Ricitos de Oro)': '#00ff00', 
                                                          'Zona Caliente': '#ff4444', 'Zona Fría': '#4444ff'},
                                       labels={'distancia_estimada_AU': 'Distancia a la Estrella (AU)', 
                                              'st_teff': 'Temperatura Estrella (K)'},
                                       title="Zona de Habitabilidad vs Temperatura Estelar")
                    fig_hab.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_hab, use_container_width=True)

            with tab3:
                st.markdown("### Ritmo de Descubrimientos")
                conteo_anual = df['disc_year'].value_counts().sort_index()
                fig_hist = px.bar(x=conteo_anual.index, y=conteo_anual.values,
                                labels={'x': 'Año', 'y': 'Descubrimientos'},
                                title="Descubrimiento de Exoplanetas por Año")
                fig_hist.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                fig_hist.update_traces(marker_color='#00e5ff')
                st.plotly_chart(fig_hist, use_container_width=True)

            if st.button("📄 Generar Reporte Científico", use_container_width=True):
                _, report = calc_instance.aplicar_exoplanetas(df)
                st.session_state.metadatos['ultimo_reporte'] = report
                st.success("✅ Reporte generado. Ve a la pestaña 'Reporte' para verlo.")
                st.code(report)

        # Genérico
        else:
            st.markdown("### Análisis Estadístico General")
            st.dataframe(df.describe(), use_container_width=True)

# === PÁGINA MACHINE LEARNING ===
elif pagina == "🤖 Machine Learning":
    if st.session_state.datos_actuales is None:
        st.warning("⚠️ No hay datos cargados. Por favor, carga datos primero.")
    else:
        st.markdown("<h1>🤖 Machine Learning</h1>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="custom-card">
                <h3 style="color: #00e5ff; margin-bottom: 1rem;">📊 Datos Disponibles</h3>
                <p><strong>Fuente:</strong> {st.session_state.fuente_actual}</p>
                <p><strong>Registros:</strong> {len(st.session_state.datos_actuales):,}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.warning("🚧 Integración con módulo ML en desarrollo. Pronto disponible: Clustering, Clasificación y Redes Neuronales.")

# === PÁGINA REPORTE ===
elif pagina == "📃 Reporte":
    st.markdown("<h1>📃 Último Reporte</h1>", unsafe_allow_html=True)
    
    if 'ultimo_reporte' in st.session_state.metadatos and st.session_state.metadatos['ultimo_reporte']:
        st.markdown("""
            <div style="background: rgba(0, 229, 255, 0.1); border: 1px solid rgba(0, 229, 255, 0.3); 
                        border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
                <h3 style="color: #00e5ff; margin-bottom: 1rem;">📄 Reporte del Último Análisis</h3>
            </div>
        """, unsafe_allow_html=True)
        st.code(st.session_state.metadatos['ultimo_reporte'], language="text")
        
        # Botón para descargar
        report_text = st.session_state.metadatos['ultimo_reporte']
        st.download_button(
            label="⬇️ Descargar Reporte",
            data=report_text,
            file_name="reporte_astroquipu.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("📭 No se ha generado ningún reporte de cálculo aún. Realiza un análisis en la sección de Cálculos.")

# --- FOOTER ---
st.markdown("""
    <div style='text-align: center; padding: 2rem 0; margin-top: 2rem; 
                border-top: 1px solid rgba(0, 229, 255, 0.2);'>
        <p style='color: rgba(224, 247, 250, 0.6); font-size: 0.9rem;'>
            🌌 <strong>AstroQuipu</strong> - Sistema de Análisis Astronómico
        </p>
        <p style='color: rgba(224, 247, 250, 0.4); font-size: 0.8rem;'>
            Desarrollado con ❤️ para la astronomía
        </p>
    </div>
""", unsafe_allow_html=True)
