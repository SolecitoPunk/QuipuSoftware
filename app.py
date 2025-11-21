import streamlit as st
import pandas as pd
import sys
import os
import importlib.util
import importlib
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- TRUCO PARA EVITAR ERROR PYCURL ---
from unittest.mock import MagicMock
sys.modules['pycurl'] = MagicMock()
# --------------------------------------

# --- LIBRERÍAS DE MACHINE LEARNING ---
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score

# --- 1. CONFIGURACIÓN DE RUTAS E IMPORTACIONES ---
current_dir = os.path.dirname(os.path.abspath(__file__))

# Añadimos rutas solo si no están ya
paths_to_add = [
    current_dir,
    os.path.join(current_dir, 'DB'),
    os.path.join(current_dir, 'Calculations'),
    os.path.join(current_dir, 'ML'),
    os.path.join(current_dir, 'Routines')
]

for p in paths_to_add:
    if p not in sys.path:
        sys.path.insert(0, p)

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

# Importamos las clases
Rutina_cls, is_rutina_ok, err_rutina = safe_import('rutinas', 'Rutina')
Calculos_cls, is_calculos_ok, err_calculos = safe_import('calculos', 'Calculos')

# --- 2. CSS PERSONALIZADO ---
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
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(10, 14, 23, 0.95) !important;
        border-right: 1px solid rgba(0, 229, 255, 0.2);
        display: block !important; /* Forzar que se vea */
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
    
    /* Inputs */
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        background: rgba(10, 14, 23, 0.8) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        color: #e0f7fa !important;
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
    
    /* Ocultar branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. INICIALIZACIÓN DE ESTADO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "🏠 Inicio"
if 'datos_actuales' not in st.session_state:
    st.session_state.datos_actuales = None
if 'fuente_actual' not in st.session_state:
    st.session_state.fuente_actual = None
if 'metadatos' not in st.session_state:
    st.session_state.metadatos = {}
if 'rutina_instance' not in st.session_state:
    if is_rutina_ok and Rutina_cls:
        st.session_state.rutina_instance = Rutina_cls()
# Estado específico para ML
if 'ml_model' not in st.session_state:
    st.session_state.ml_model = None
if 'ml_history' not in st.session_state:
    st.session_state.ml_history = None
if 'ml_exo_res' not in st.session_state:
    st.session_state.ml_exo_res = None

# --- 4. BARRA LATERAL ---
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
                try:
                    importlib.reload(sys.modules[module_name])
                except:
                    pass
        Rutina_cls, is_rutina_ok, _ = safe_import('rutinas', 'Rutina', force_reload=True)
        if is_rutina_ok and Rutina_cls:
            st.session_state.rutina_instance = Rutina_cls()
        st.session_state.pagina = "🏠 Inicio"
        st.rerun()
    
    st.markdown("<hr style='border-color: rgba(0, 229, 255, 0.2); margin: 1rem 0;'>", unsafe_allow_html=True)
    
    # Navegación
    pagina = st.radio(
        "Navegación",
        ["🏠 Inicio", "📂 Cargar Datos", "🔭 Cálculos", "∑  Calculadoras", "☶ Machine Learning", "☖  Reporte"],
        key="nav_radio",
        label_visibility="collapsed"
    )
    st.session_state.pagina = pagina
    
    st.markdown("<hr style='border-color: rgba(0, 229, 255, 0.2); margin: 1rem 0;'>", unsafe_allow_html=True)
    
    # Estado de datos
    st.markdown("###  ▁ ▂ ▃ Estado de Datos")
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

# --- 5. CONTENIDO PRINCIPAL ---

# === PÁGINA DE INICIO ===
if pagina == "◈ Inicio":
    st.markdown("""
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">◉  AstroQuipu</h1>
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
                <h3 style="color: #00e5ff; margin-bottom: 1rem;">❀ Análisis</h3>
                <p style="font-size: 0.9rem;">Cálculos cosmológicos, orbitales y visualizaciones 3D interactivas.</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="custom-card">
                <h3 style="color: #00e5ff; margin-bottom: 1rem;">☲ Machine Learning</h3>
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
        3: "❀ DESI - Objetos del cosmos profundo",
        4: " Ⓝ NASA ESI - Exoplanetas",
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
                    if st.session_state.rutina_instance:
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
                    else:
                        st.error("❌ Error: Instancia de Rutina no inicializada.")
                except Exception as e:
                    st.error(f"❌ Error al consultar {nombre_corto}: {e}")

    # NASA ESI
    elif opcion_seleccionada == 4:
        st.markdown("### 🪐 NASA ESI - Exoplanetas")
        st.markdown("Consulta la base de datos de exoplanetas de la NASA (datos recientes con radio conocido).")
        
        if st.button("🔍 Consultar NASA ESI", key="btn_nasa_esi", use_container_width=True):
            with st.spinner("Contactando a NASA Exoplanet Archive..."):
                try:
                    if st.session_state.rutina_instance:
                        resultado = st.session_state.rutina_instance.base_datos.conectar(source="NASA ESI")
                        if resultado is not None:
                            df = resultado.to_pandas() if hasattr(resultado, 'to_pandas') else resultado
                            st.session_state.datos_actuales = df
                            st.session_state.fuente_actual = "NASA ESI"
                            st.success(f"✅ ¡Éxito! Se cargaron {len(df)} exoplanetas.")
                            st.rerun()
                        else:
                            st.error("❌ No se obtuvieron resultados.")
                    else:
                         st.error("❌ Error: Instancia de Rutina no inicializada.")
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
                    if st.session_state.rutina_instance:
                        resultado = st.session_state.rutina_instance.base_datos.conectar(source="NEO", object_name=seleccion_neo)
                        if resultado is not None:
                            df = resultado.to_pandas() if hasattr(resultado, 'to_pandas') else resultado
                            st.session_state.datos_actuales = df
                            st.session_state.fuente_actual = f"NEO - {seleccion_neo}"
                            st.success(f"✅ Datos orbitales de {seleccion_neo} descargados correctamente.")
                            st.rerun()
                        else:
                            st.error("❌ No se obtuvieron resultados.")
                    else:
                        st.error("❌ Error: Instancia de Rutina no inicializada.")
                except Exception as e:
                    st.error(f"❌ Error en la consulta: {str(e)}")

# === PÁGINA DE CÁLCULOS ===
elif pagina == "🔭 Cálculos":
    if st.session_state.datos_actuales is None:
        st.warning("⚠️ No hay datos cargados. Por favor, carga datos primero desde la sección 'Cargar Datos'.")
    elif not is_calculos_ok or not Calculos_cls:
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
        
        # SDSS (Cosmología)
        if source and "SDSS" in source:
            tab1, tab2, tab3 = st.tabs(["▁ ▂ ▃ Estadísticas", "『 』Mapa Galaxia", "Σ  Cálculos"])
            
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
                st.markdown("### ⠝ ⠜ ⠛ La Telaraña Cósmica")
                if st.button("⠝ ⠜ ⠛Generar Mapa", key="btn_mapa_3d", use_container_width=True):
                    with st.spinner("Triangulando posiciones en el universo..."):
                        df_3d = calc_instance.generar_coordenadas_cartesianas(df)
                        if df_3d is not None:
                            fig_3d = px.scatter_3d(df_3d, x='x_coord', y='y_coord', z='z_coord',
                                                 color='z', opacity=0.7,
                                                 title="Mapa de  nuestro Universo  Observable (Mpc)",
                                                 color_continuous_scale='Viridis')
                            fig_3d.update_traces(marker=dict(size=3))
                            fig_3d.update_layout(template="plotly_dark", scene=dict(aspectmode='data'),
                                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                            st.plotly_chart(fig_3d, use_container_width=True)
                            st.success("⠝ ⠜ ⠛ Mapa generado. Usa el mouse para rotar y hacer zoom.")
                        else:
                            st.error("Faltan columnas RA/DEC/Z para generar el mapa.")

            with tab3:
                st.markdown("### Aplicar Cálculos Numéricos")
                if st.button("Σ  Distancias Hubble", use_container_width=True):
                    new_df, report = calc_instance.aplicar_cosmologia(df)
                    st.session_state.datos_actuales = new_df
                    st.session_state.metadatos['ultimo_reporte'] = report
                    st.success("✅ Cálculos aplicados correctamente.")
                    st.dataframe(new_df[['z', 'Distancia_Hubble_Mpc', 'Velocidad_Recesion_km_s']].head(10))

        # DESI (Fotometría Deep Sky)
        elif source and "DESI" in source:
            st.info(f"🔭 Analizando fotometría de {len(df)} objetos profundos.")
            
            if 'mag_g' not in df.columns:
                df, _ = calc_instance.aplicar_fotometria_desi(df)
                st.session_state.datos_actuales = df

            tab1, tab2, tab3 = st.tabs(["🔴🟣🟠🟢 Diagrama Color-Color", "『 』Mapa del Cielo", "☱ Clasificación"])
            
            with tab1:
                st.markdown("### Diagrama de Diagnóstico Astronómico")
                st.markdown("""
                El cruce de colores nos dice qué tipo de objetos estamos observando:
                - **Arriba/Izquierda:** Galaxias Rojas (Elípticas / Viejas)
                - **Abajo/Derecha:** Galaxias Azules (Espirales / Jóvenes)
                - **Puntos aislados:** Posibles Quásares o Estrellas
                """)
                
                if 'color_g_r' in df.columns and 'color_r_z' in df.columns:
                    color_col = 'type' if 'type' in df.columns else 'color_g_r'
                    
                    fig_color = px.scatter(df, x="color_g_r", y="color_r_z",
                                         color=color_col, opacity=0.6,
                                         hover_data=['ra', 'dec', 'mag_g'],
                                         labels={'color_g_r': 'Color g - r (Verde - Rojo)', 
                                                 'color_r_z': 'Color r - z (Rojo - Infrarrojo)'},
                                         title="Diagrama Color-Color (g-r vs r-z)")
                    fig_color.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_color, use_container_width=True)
                else:
                    st.warning("Faltan datos de flujo (g, r, z) para calcular colores.")

            with tab2:
                st.markdown("### Distribución Espacial en el Cielo")
                st.markdown("Densidad de objetos en las coordenadas observadas.")
                
                if 'ra' in df.columns and 'dec' in df.columns:
                    fig_sky = px.density_heatmap(df, x="ra", y="dec",
                                               nbinsx=30, nbinsy=30,
                                               labels={'ra': 'Ascensión Recta (RA)', 'dec': 'Declinación (DEC)'},
                                               title="Densidad de Objetos DESI",
                                               color_continuous_scale='Viridis')
                    fig_sky.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_sky, use_container_width=True)

            with tab3:
                st.markdown("### Tipos Morfológicos")
                if 'type' in df.columns:
                    conteo = df['type'].value_counts()
                    fig_bar = px.bar(x=conteo.index, y=conteo.values,
                                   labels={'x': 'Tipo Objeto', 'y': 'Cantidad'},
                                   title="Clasificación Morfológica (Tractor Type)",
                                   color=conteo.values, color_continuous_scale='Bluered_r')
                    fig_bar.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_bar, use_container_width=True)
                    
                    st.info("""
                    **Tipos de objetos:**
                    - **PSF:** Puntos de luz (probablemente Estrellas o Quásares lejanos)
                    - **REX/EXP/DEV:** Objetos extendidos (Galaxias redondas, discos o irregulares)
                    """)
                else:
                    st.warning("No se encontró la columna 'type'.")

            if st.button("⎔ Generar Reporte Fotométrico", use_container_width=True):
                _, report = calc_instance.aplicar_fotometria_desi(df)
                st.session_state.metadatos['ultimo_reporte'] = report
                st.success("✅ Reporte generado. Ve a la pestaña 'Reporte' para verlo.")
                st.code(report)

        # NEO
        elif source and "NEO" in source:
            tab1, tab2 = st.tabs([" ❂ Simulador Orbital", " Parámetros"])
            
            with tab1:
                st.markdown("### Simulación Orbital Futura")
                col_sim1, col_sim2 = st.columns([1, 2])
                with col_sim1:
                    dias_futuro = st.number_input("Días a simular:", min_value=1, max_value=36500, value=365, step=30)
                    run_sim = st.button(" ❂ Simular Trayectoria", use_container_width=True)
                
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
                if st.button("∑ Calcular Velocidades Medias", use_container_width=True):
                    new_df, report = calc_instance.aplicar_orbitales(df)
                    st.session_state.datos_actuales = new_df
                    st.session_state.metadatos['ultimo_reporte'] = report
                    st.success("✅ Cálculos aplicados.")
                    st.rerun()

        # NASA ESI - Exoplanetas
        elif source and "NASA ESI" in source:
            if 'Clase_Planeta' not in df.columns:
                df, _ = calc_instance.aplicar_exoplanetas(df)
                st.session_state.datos_actuales = df

            st.info(f"🪐 Analizando {len(df)} exoplanetas confirmados.")
            tab1, tab2, tab3 = st.tabs(["🔵 Masa vs Radio", "☀️ Zona Habitable", "Descubrimientos"])
            
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

            if st.button("📄 Reporte", use_container_width=True):
                _, report = calc_instance.aplicar_exoplanetas(df)
                st.session_state.metadatos['ultimo_reporte'] = report
                st.success("✅ Reporte generado. Ve a la pestaña 'Reporte' para verlo.")
                st.code(report)

        # Genérico
        else:
            st.markdown("### Análisis Estadístico General")
            st.dataframe(df.describe(), use_container_width=True)

# === PÁGINA CALCULADORAS (NUEVA SECCIÓN) ===
elif pagina == "∑ Calculadoras":
    st.markdown("<h1>∑ Calculadoras Astrofísicas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: rgba(224, 247, 250, 0.8);'>Herramientas rápidas para cálculos fundamentales.</p>", unsafe_allow_html=True)
    
    calc_instance = Calculos_cls() if Calculos_cls else None
    if not calc_instance:
        st.error("No se pudo cargar el módulo de cálculos.")
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["🌌 Hubble", "🔴 Redshift", "🔄 V. Angular", "㊂ Orbital"])

        # 1. Calculadora Hubble
        with tab1:
            st.markdown("### Constante de Hubble ($H_0$)")
            st.write("Calcula la tasa de expansión del universo basada en velocidad y distancia.")
            
            col1, col2 = st.columns(2)
            with col1:
                v_rec = st.number_input("Velocidad de Recesión (km/s)", value=7000.0, step=100.0)
            with col2:
                d_mpc = st.number_input("Distancia (Mpc)", value=100.0, step=10.0)
            
            if st.button("Calcular H0", key="btn_h0"):
                h0_val = calc_instance.calc_basic_hubble(v_rec, d_mpc)
                st.success(f"✅ Constante de Hubble calculada: **{h0_val:.2f} km/s/Mpc**")
                
                st.markdown("""
                <div style="background: rgba(0, 229, 255, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                    <small>📝 Nota: El valor aceptado actualmente varía entre 67 y 74 km/s/Mpc.</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Dato interesante sobre distancias
                if d_mpc > 0:
                    dist_ly = d_mpc * 3.262e6
                    st.info(f"ℹ️ {d_mpc} Mpc equivalen a aproximadamente **{dist_ly:,.0f} años luz**.")

        # 2. Calculadora Redshift
        with tab2:
            st.markdown("### Desplazamiento al Rojo ($z$)")
            st.write("Determina el desplazamiento espectral comparando longitudes de onda.")
            
            col1, col2 = st.columns(2)
            with col1:
                l_obs = st.number_input("Longitud de onda observada (nm)", value=658.0, step=0.1)
            with col2:
                l_emit = st.number_input("Longitud de onda emitida (nm)", value=656.3, step=0.1, help="Ej: H-alpha es 656.3 nm")
            
            if st.button("Calcular Redshift", key="btn_z"):
                z_val = calc_instance.calc_basic_redshift(l_obs, l_emit)
                st.success(f"✅ Redshift (z): **{z_val:.5f}**")
                
                if z_val > 0:
                    st.write("🔴 El objeto se aleja (Redshift).")
                elif z_val < 0:
                    st.write("🔵 El objeto se acerca (Blueshift).")

        # 3. Calculadora Velocidad Angular
        with tab3:
            st.markdown("### Velocidad Angular ($\omega$)")
            st.write("Relación entre velocidad lineal y radio.")
            
            col1, col2 = st.columns(2)
            with col1:
                v_lin = st.number_input("Velocidad lineal (km/s)", value=30.0)
            with col2:
                r_km = st.number_input("Radio de órbita (km)", value=150000000.0)
            
            if st.button("Calcular Omega", key="btn_w"):
                w_val = calc_instance.calc_basic_angular_vel(v_lin, r_km)
                st.success(f"✅ Velocidad Angular: **{w_val:.2e} rad/s**")

        # 4. Calculadora Orbital
        with tab4:
            st.markdown("### Velocidad Orbital ($v$)")
            st.write("Velocidad necesaria para mantener una órbita circular estable.")
            
            col1, col2 = st.columns(2)
            with col1:
                m_central = st.number_input("Masa central (kg)", value=1.989e30, format="%.2e")
            with col2:
                r_orbita_m = st.number_input("Radio de órbita (m)", value=1.496e11, format="%.2e")
            
            if st.button("Calcular Velocidad Orbital", key="btn_orb"):
                v_orb = calc_instance.calc_basic_orbital(m_central, r_orbita_m)
                st.success(f"✅ Velocidad Orbital: **{v_orb/1000:.2f} km/s**")
                st.info("Usando G = 6.67430e-11")

# === PÁGINA MACHINE LEARNING (MODIFICADA) ===
elif pagina == "≣ Machine Learning":
    if st.session_state.datos_actuales is None:
        st.warning("⚠️ No hay datos cargados. Por favor, carga datos primero.")
    else:
        df = st.session_state.datos_actuales.copy()
        cols = df.columns.tolist()
        
        st.markdown("<h1>🤖 Laboratorio de Inteligencia Artificial</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: rgba(224, 247, 250, 0.8);'>Modelos predictivos y de agrupamiento avanzados.</p>", unsafe_allow_html=True)

        # --- DETECTOR DE CONTEXTO ---
        # Sugiere el tipo de proyecto basado en las columnas disponibles
        project_type = "Generico"
        
        # Caso 1: NEO (Asteroides) - Detecta elementos orbitales
        if {'a', 'e', 'i'}.issubset(cols) or {'a', 'e', 'incl'}.issubset(cols):
            project_type = "NEO_Clustering"
            st.success("🚀 Contexto Detectado: Dinámica Orbital de Asteroides")
        
        # Caso 2: NASA Exoplanetas - Detecta radio/periodo
        elif {'pl_rade', 'pl_orbper'}.issubset(cols):
            project_type = "Exo_Regression"
            st.success("🪐 Contexto Detectado: Astrofísica de Exoplanetas")
            
        # Caso 3: SDSS - Detecta magnitudes y redshift
        elif {'u', 'g', 'r', 'i', 'z'}.issubset(cols) and ('class' in cols or 'z' in cols):
             project_type = "SDSS_PhotoZ"
             st.success("🌌 Contexto Detectado: Cosmología SDSS (Redshift Fotométrico)")

        # Caso 4: DESI/SDSS Generico - Detecta flujos o magnitudes
        elif any(x in cols for x in ['flux_g', 'mag_g', 'flux_r']):
            project_type = "DeepSpace_Clustering"
            st.success("🔭 Contexto Detectado: Fotometría de Espacio Profundo")

        # --- INTERFACES DE PROYECTO ---
        
        # === PROYECTO A: CLUSTERING DE FAMILIAS DE ASTEROIDES ===
        if project_type == "NEO_Clustering":
            st.markdown("""
            ### ☄️ Proyecto A: Detección de Familias de Asteroides
            **Objetivo:** Utilizar algoritmos no supervisados (K-Means) para encontrar grupos de asteroides que comparten origen (familias colisionales).
            """)
            
            col_params, col_viz = st.columns([1, 2])
            
            with col_params:
                st.markdown("#### Configuración del Modelo")
                n_clusters = st.slider("Número de Familias (k)", 2, 10, 3)
                
                # Selección de features (intenta auto-detectar)
                c_a = 'a' if 'a' in cols else cols[0]
                c_e = 'e' if 'e' in cols else cols[1]
                c_i = 'i' if 'i' in cols else ('incl' if 'incl' in cols else cols[2])
                
                features = st.multiselect("Variables de Agrupamiento", cols, default=[c_a, c_e, c_i])
                
                if st.button("🚀 Ejecutar Clustering", use_container_width=True):
                    if len(features) >= 2:
                        # Preprocesamiento
                        X = df[features].dropna()
                        scaler = StandardScaler()
                        X_scaled = scaler.fit_transform(X)
                        
                        # Modelo
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                        labels = kmeans.fit_predict(X_scaled)
                        
                        # Guardar resultado temporal
                        df_res = df.loc[X.index].copy()
                        df_res['Cluster'] = labels.astype(str)
                        st.session_state.ml_result = df_res
                        st.success(f"✅ Se encontraron {n_clusters} familias potenciales.")
                    else:
                        st.error("Selecciona al menos 2 variables.")

            with col_viz:
                if 'ml_result' in st.session_state and project_type == "NEO_Clustering":
                    res = st.session_state.ml_result
                    st.markdown("#### 🌌 Visualización 3D de Familias")
                    
                    # Gráfico 3D
                    fig_3d = px.scatter_3d(res, x=c_a, y=c_e, z=c_i,
                                         color='Cluster', opacity=0.7,
                                         title="Familias de Asteroides Detectadas",
                                         labels={c_a: 'Semieje Mayor (a)', c_e: 'Excentricidad (e)', c_i: 'Inclinación (i)'})
                    fig_3d.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_3d, use_container_width=True)

        # === PROYECTO F: PREDICCIÓN DE MASA (RED NEURONAL) ===
        elif project_type == "Exo_Regression":
            st.markdown("""
            ### ⚖️ Proyecto F: Predicción de Masa Planetaria (Deep Learning)
            **Objetivo:** Entrenar una Red Neuronal para predecir la masa de un exoplaneta basándose en su radio y periodo.
            """)
            
            col_input, col_train = st.columns(2)
            
            with col_input:
                st.markdown("#### Variables de Entrada (X)")
                default_x = [c for c in ['pl_rade', 'pl_orbper', 'st_teff'] if c in cols]
                features_x = st.multiselect("Selecciona Features", cols, default=default_x)
                
                st.markdown("#### Objetivo (Y)")
                target_y = st.selectbox("Variable a Predecir", cols, index=cols.index('pl_bmasse') if 'pl_bmasse' in cols else 0)
                
            with col_train:
                st.markdown("#### Hiperparámetros de la Red")
                hidden_layers = st.slider("Complejidad (Neuronas Ocultas)", 10, 100, 50)
                epochs = st.slider("Iteraciones (Epochs)", 100, 1000, 500)
                
                if st.button("🧠 Entrenar Red Neuronal", use_container_width=True):
                    if features_x and target_y:
                        # Preparación de datos
                        data_ml = df[features_x + [target_y]].dropna()
                        X = data_ml[features_x]
                        y = data_ml[target_y]
                        
                        # Guardar nombres para uso posterior
                        nombres_planetas = df.loc[data_ml.index, 'pl_name'] if 'pl_name' in df.columns else data_ml.index

                        X_train, X_test, y_train, y_test, name_train, name_test = train_test_split(X, y, nombres_planetas, test_size=0.2, random_state=42)
                        
                        # Escalamiento (Vital para Redes Neuronales)
                        scaler_x = StandardScaler()
                        scaler_y = StandardScaler()
                        
                        X_train_sc = scaler_x.fit_transform(X_train)
                        X_test_sc = scaler_x.transform(X_test)
                        y_train_sc = scaler_y.fit_transform(y_train.values.reshape(-1, 1)).ravel()
                        y_test_sc = scaler_y.transform(y_test.values.reshape(-1, 1)).ravel()
                        
                        # Modelo
                        model = MLPRegressor(hidden_layer_sizes=(hidden_layers, hidden_layers//2),
                                           max_iter=epochs, random_state=42, learning_rate_init=0.001)
                        
                        with st.spinner("Entrenando red neuronal..."):
                            model.fit(X_train_sc, y_train_sc)
                            
                        # Predicciones
                        y_pred_sc = model.predict(X_test_sc)
                        y_pred = scaler_y.inverse_transform(y_pred_sc.reshape(-1, 1)).ravel()
                        
                        # Métricas
                        r2 = r2_score(y_test, y_pred)
                        
                        # Guardar TODO en session_state para la parte interactiva
                        st.session_state.ml_exo_res = {
                            'y_test': y_test, 'y_pred': y_pred, 'r2': r2, 'model': model,
                            'names': name_test, 'scaler_y': scaler_y, 'inputs': features_x, 'target': target_y
                        }
                        st.success(f"✅ Entrenamiento finalizado. R² Score: {r2:.4f}")
                    else:
                        st.error("Faltan variables.")

            # Visualización de Resultados
            if 'ml_exo_res' in st.session_state and project_type == "Exo_Regression":
                res = st.session_state.ml_exo_res
                
                st.markdown("---")
                col_res_viz, col_res_ind = st.columns(2)
                
                with col_res_viz:
                    st.markdown("#### 📉 Evaluación Global")
                    fig_reg = px.scatter(x=res['y_test'], y=res['y_pred'], 
                                       hover_name=res['names'],
                                       labels={'x': 'Masa Real', 'y': 'Masa Predicha por IA'},
                                       title=f"Predicción vs Realidad (Ajuste: {res['r2']:.2f})")
                    min_val = min(res['y_test'].min(), res['y_pred'].min())
                    max_val = max(res['y_test'].max(), res['y_pred'].max())
                    fig_reg.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val,
                                    line=dict(color="red", dash="dash"))
                    fig_reg.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_reg, use_container_width=True)

                # --- NUEVA SECCIÓN: PREDICCIÓN INDIVIDUAL ---
                with col_res_ind:
                    st.markdown("#### 🔮 Oráculo Planetario")
                    st.write("Selecciona un planeta del set de prueba para ver qué tan cerca estuvo la IA.")
                    
                    # Crear diccionario para el selectbox
                    test_indices = res['y_test'].index
                    test_names = res['names']
                    opciones = {i: f"{name} (ID: {i})" for i, name in zip(test_indices, test_names)}
                    
                    seleccion_id = st.selectbox("Selecciona Planeta:", list(opciones.keys()), format_func=lambda x: opciones[x])
                    
                    if seleccion_id:
                        # Encontrar los valores reales y predichos
                        # Nota: y_test es una Serie, podemos acceder por índice
                        real = res['y_test'].loc[seleccion_id]
                        
                        # Para encontrar el predicho, necesitamos saber la posición en el array numpy
                        # Esto es un poco truculento porque y_pred es un array sin índices
                        pos_array = list(test_indices).index(seleccion_id)
                        pred = res['y_pred'][pos_array]
                        
                        error = abs(real - pred)
                        error_pct = (error / real) * 100 if real != 0 else 0
                        
                        st.metric(label="Masa Real", value=f"{real:.2f} M_tierra")
                        st.metric(label="Predicción IA", value=f"{pred:.2f} M_tierra", delta=f"{pred-real:.2f}")
                        
                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 5px;">
                            <strong>Margen de Error:</strong> {error_pct:.1f}%
                        </div>
                        """, unsafe_allow_html=True)

        # === PROYECTO G: SDSS PHOTO-Z (RED NEURONAL) ===
        elif project_type == "SDSS_PhotoZ":
            st.markdown("""
            ### 🌌 Proyecto G: Estimación de Redshift Fotométrico (Photo-z)
            **Objetivo:** Entrenar una IA para calcular la distancia ($z$) a galaxias usando solo sus colores ($u,g,r,i,z$).
            """)
            
            # Inputs automáticos SDSS
            features_sdss = ['u', 'g', 'r', 'i', 'z']
            target_sdss = 'z' if 'z' in cols else 'redshift'
            
            col_sdss_conf, col_sdss_res = st.columns(2)
            
            with col_sdss_conf:
                st.markdown("#### Configuración")
                st.write(f"**Features:** {features_sdss}")
                st.write(f"**Objetivo:** {target_sdss}")
                
                neuronas = st.slider("Neuronas por Capa", 20, 200, 100)
                
                if st.button("🚀 Calcular Photo-z", use_container_width=True):
                    # Preproceso
                    data_z = df[features_sdss + [target_sdss]].dropna()
                    # Limpiar datos malos (z < 0 o magnitudes extremas)
                    data_z = data_z[(data_z[target_sdss] > 0) & (data_z[target_sdss] < 1)] 
                    
                    X = data_z[features_sdss]
                    y = data_z[target_sdss]
                    
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                    
                    scaler = StandardScaler()
                    X_train_s = scaler.fit_transform(X_train)
                    X_test_s = scaler.transform(X_test)
                    
                    model_z = MLPRegressor(hidden_layer_sizes=(neuronas, neuronas, neuronas//2), 
                                         max_iter=500, random_state=42)
                    
                    with st.spinner("Aprendiendo la estructura del universo..."):
                        model_z.fit(X_train_s, y_train)
                        
                    y_pred = model_z.predict(X_test_s)
                    r2 = r2_score(y_test, y_pred)
                    mse = mean_squared_error(y_test, y_pred)
                    
                    st.session_state.ml_sdss_res = {'y_test': y_test, 'y_pred': y_pred, 'r2': r2, 'mse': mse}
                    st.success(f"Modelo entrenado. R²: {r2:.4f}")

            with col_sdss_res:
                if 'ml_sdss_res' in st.session_state:
                    res = st.session_state.ml_sdss_res
                    fig_z = px.scatter(x=res['y_test'], y=res['y_pred'], opacity=0.5,
                                     labels={'x': 'Redshift Espectroscópico (Real)', 'y': 'Photo-z (IA)'},
                                     title="Calidad de la Estimación Photo-z")
                    fig_z.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line=dict(color="red"))
                    fig_z.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_z, use_container_width=True)
                    
                    st.info(f"Error Medio Cuadrático (MSE): {res['mse']:.5f}")

        # === PROYECTO C: CLASIFICACIÓN DESI (COLOR-COLOR) ===
        elif project_type == "DeepSpace_Clustering":
            st.markdown("""
            ### 🔭 Proyecto C: Clasificación Espectral (Deep Space)
            **Objetivo:** Separar Estrellas, Galaxias y Quásares usando diagramas de color ($g-r$ vs $r-z$).
            """)
            
            # Asegurar que existen colores
            calc_instance = Calculos_cls()
            if 'color_g_r' not in df.columns:
                df, _ = calc_instance.aplicar_fotometria_desi(df)
            
            col_viz_desi, col_conf_desi = st.columns([2, 1])
            
            with col_conf_desi:
                st.markdown("#### Parámetros")
                k_desi = st.slider("Grupos Esperados", 2, 5, 3, help="Tip: 3 grupos suelen ser Estrellas, Galaxias Rojas y Azules")
                if st.button("🎨 Analizar Espectro", use_container_width=True):
                    cols_color = ['color_g_r', 'color_r_z']
                    data_color = df[cols_color].dropna()
                    
                    kmeans = KMeans(n_clusters=k_desi, random_state=42)
                    labels = kmeans.fit_predict(data_color)
                    
                    df.loc[data_color.index, 'Spectral_Cluster'] = labels.astype(str)
                    st.session_state.datos_actuales = df # Guardar en sesión
                    st.success("Clasificación completada.")

            with col_viz_desi:
                if 'Spectral_Cluster' in df.columns:
                    fig_color = px.scatter(df, x="color_g_r", y="color_r_z",
                                         color="Spectral_Cluster", opacity=0.6,
                                         title="Diagrama Color-Color Clasificado",
                                         labels={'color_g_r': 'Color g-r', 'color_r_z': 'Color r-z'})
                    fig_color.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_color, use_container_width=True)

        # === OPCIÓN GENÉRICA ===
        else:
            st.info("No se detectó un dataset especializado conocido. Usa el modo genérico.")
            # (Aquí podrías poner un selector genérico de X/Y si quisieras)

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
