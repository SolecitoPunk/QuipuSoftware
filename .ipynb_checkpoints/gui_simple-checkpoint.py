import streamlit as st
import pandas as pd
import sys
import os
import importlib.util
import importlib

# Configurar el path para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Variable para almacenar errores de importación
import_errors = {}

# Función auxiliar mejorada para importar módulos
def safe_import(module_path, class_name, force_reload=False):
    """Intenta importar un módulo y retorna la clase o una versión dummy."""
    try:
        # Si force_reload, recargar el módulo
        if force_reload and module_path in sys.modules:
            importlib.reload(sys.modules[module_path])
        
        # Intentar importación directa
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        return cls, True, None
    except Exception as e:
        # Guardar el error para debugging
        import_errors[module_path] = str(e)
        return None, False, str(e)

# Botón para recargar módulos (útil después de modificar archivos)
if st.sidebar.button("🔄 Recargar Módulos"):
    # Limpiar caché de Streamlit
    st.cache_data.clear()
    st.cache_resource.clear()
    
    # Forzar recarga de módulos
    for module_name in ['DB.entrada', 'DB.BaseDatos', 'Calculations.Calculations', 'ML.MachineL']:
        if module_name in sys.modules:
            del sys.modules[module_name]
    
    st.rerun()

# Importar módulos del proyecto con manejo de errores
Entrada, DB_ENTRADA_OK, entrada_error = safe_import('DB.entrada', 'Entrada')
if not DB_ENTRADA_OK:
    class Entrada:
        def leerDatos(self):
            st.error("Módulo DB.entrada no disponible")
            return None

BaseDatos, DB_BASE_OK, base_error = safe_import('DB.BaseDatos', 'BaseDatos')
if not DB_BASE_OK:
    class BaseDatos:
        def conectar(self, **kwargs):
            st.error("Módulo DB.BaseDatos no disponible")
            return None
        def guardardatos(self, data, source):
            return None

MenuCalculos, CALC_AVAILABLE, calc_error = safe_import('Calculations.Calculations', 'MenuCalculos')
if not CALC_AVAILABLE:
    class MenuCalculos:
        def mostrar_menu(self, datos):
            st.warning("⚠️ Módulo de Cálculos no disponible")
            st.error(f"Error: {calc_error}")

MenuML, ML_AVAILABLE, ml_error = safe_import('ML.MachineL', 'MenuML')
if not ML_AVAILABLE:
    class MenuML:
        def mostrar_menu(self, datos):
            st.warning("⚠️ Módulo de ML no disponible")
            st.error(f"Error: {ml_error}")

DB_AVAILABLE = DB_ENTRADA_OK and DB_BASE_OK

# Configuración de la página
st.set_page_config(
    page_title="AstroQuipu - Sistema de Análisis Astronómico",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar session_state
if 'datos_actuales' not in st.session_state:
    st.session_state.datos_actuales = None
if 'fuente_actual' not in st.session_state:
    st.session_state.fuente_actual = None
if 'metadatos' not in st.session_state:
    st.session_state.metadatos = {}
if 'entrada' not in st.session_state:
    st.session_state.entrada = Entrada()
if 'base_datos' not in st.session_state:
    st.session_state.base_datos = BaseDatos()
if 'menu_calculos' not in st.session_state:
    st.session_state.menu_calculos = MenuCalculos()
if 'menu_ml' not in st.session_state:
    st.session_state.menu_ml = MenuML()
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = "inicio"

# Título principal
st.title("🌌 AstroQuipu - Sistema de Análisis Astronómico Educativo")

# Mostrar estado de módulos con más detalles
with st.expander("🔧 Estado de Módulos del Sistema"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("DB")
        if DB_AVAILABLE:
            st.success("✅ Disponible")
        else:
            st.error("❌ No disponible")
            if 'DB.entrada' in import_errors:
                st.code(import_errors['DB.entrada'], language='text')
            if 'DB.BaseDatos' in import_errors:
                st.code(import_errors['DB.BaseDatos'], language='text')
    
    with col2:
        st.subheader("Cálculos")
        if CALC_AVAILABLE:
            st.success("✅ Disponible")
        else:
            st.warning("⚠️ No disponible")
            if 'Calculations.Calculations' in import_errors:
                st.code(import_errors['Calculations.Calculations'], language='text')
    
    with col3:
        st.subheader("ML")
        if ML_AVAILABLE:
            st.success("✅ Disponible")
        else:
            st.warning("⚠️ No disponible")
            if 'ML.MachineL' in import_errors:
                st.code(import_errors['ML.MachineL'], language='text')
    
    # Información del sistema
    st.markdown("---")
    st.write("**Información del Sistema:**")
    st.write(f"- Python Path: `{current_dir}`")
    st.write(f"- Directorio actual: `{os.getcwd()}`")

st.markdown("---")

# Sidebar para navegación
with st.sidebar:
    st.header("📂 Navegación")
    
    if st.session_state.datos_actuales is None:
        pagina = st.radio(
            "Seleccione una opción:",
            ["🏠 Inicio", "📁 Cargar Datos"],
            key="navegacion_principal"
        )
    else:
        pagina = st.radio(
            "Seleccione una opción:",
            ["🏠 Inicio", "📁 Cargar Datos", "📊 Ver Datos", "🔬 Cálculos", "🤖 Machine Learning"],
            key="navegacion_completa"
        )
    
    # Información del estado actual
    st.markdown("---")
    st.subheader("📈 Estado del Sistema")
    if st.session_state.datos_actuales is not None:
        st.success("✅ Datos cargados")
        st.info(f"**Fuente:** {st.session_state.fuente_actual}")
        st.info(f"**Registros:** {len(st.session_state.datos_actuales)}")
        st.info(f"**Columnas:** {len(st.session_state.datos_actuales.columns)}")
    else:
        st.warning("⚠️ No hay datos cargados")

# ==================== PÁGINA DE INICIO ====================
if pagina == "🏠 Inicio":
    st.header("Bienvenido a AstroQuipu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 ¿Qué es AstroQuipu?")
        st.write("""
        AstroQuipu es un sistema educativo para el análisis de datos astronómicos.
        Permite cargar datos de diferentes fuentes y realizar análisis científicos
        avanzados de forma intuitiva.
        """)
        
        st.subheader("📚 Fuentes de Datos Disponibles")
        st.markdown("""
        - 📁 **Archivos Locales** (CSV/DAT)
        - 🌌 **SDSS** - Sloan Digital Sky Survey
        - 🔭 **DESI** - Dark Energy Spectroscopic Instrument
        - 🪐 **NASA ESI** - Exoplanet Systems
        - ☄️ **NEO** - Near-Earth Objects
        """)
    
    with col2:
        st.subheader("🔧 Capacidades del Sistema")
        st.markdown("""
        **Análisis de Datos:**
        - Estadísticas descriptivas
        - Visualizaciones interactivas
        - Filtrado y exploración de datos
        
        **Cálculos Astronómicos:**
        - Cálculos de distancias
        - Análisis espectral
        - Métricas científicas
        
        **Machine Learning:**
        - Clustering de objetos
        - Clasificación automática
        - Detección de patrones
        """)
    
    st.markdown("---")
    st.info("👈 **Comienza seleccionando 'Cargar Datos' en el menú lateral**")

# ==================== PÁGINA DE CARGA DE DATOS ====================
elif pagina == "📁 Cargar Datos":
    st.header("📂 Cargar Datos Astronómicos")
    
    # Selector de fuente
    fuente = st.selectbox(
        "Seleccione la fuente de datos:",
        ["Seleccione una opción...", "Archivos Locales (CSV/DAT)", "SDSS - Galaxias y Espectros", 
         "DESI - Cosmos Profundo", "NASA ESI - Exoplanetas", "NEO - Asteroides y Cometas"],
        key="selector_fuente"
    )
    
    # ===== ARCHIVOS LOCALES =====
    if fuente == "Archivos Locales (CSV/DAT)":
        st.subheader("📁 Cargar desde archivo local")
        
        uploaded_file = st.file_uploader(
            "Seleccione un archivo CSV o DAT",
            type=['csv', 'dat'],
            key="file_uploader"
        )
        
        if uploaded_file is not None:
            if st.button("🚀 Cargar Datos", key="btn_cargar_local"):
                with st.spinner("Cargando datos..."):
                    try:
                        # Intentar leer el archivo
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file)
                        else:
                            df = pd.read_csv(uploaded_file, delimiter='\t')
                        
                        st.session_state.datos_actuales = df
                        st.session_state.fuente_actual = "local"
                        st.session_state.metadatos['archivo'] = uploaded_file.name
                        
                        st.success(f"✅ Datos cargados exitosamente: {len(df)} registros")
                        st.balloons()
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error al cargar el archivo: {str(e)}")
    
    # ===== SDSS =====
    elif fuente == "SDSS - Galaxias y Espectros":
        st.subheader("🌌 SDSS - Sloan Digital Sky Survey")
        st.write("Consulta el catálogo de galaxias y espectros del SDSS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ra = st.number_input("Right Ascension (RA) [grados]", value=180.0, min_value=0.0, max_value=360.0)
            dec = st.number_input("Declination (DEC) [grados]", value=0.0, min_value=-90.0, max_value=90.0)
        
        with col2:
            z_min = st.number_input("Redshift mínimo (z-min)", value=0.05, min_value=0.0, max_value=10.0)
            z_max = st.number_input("Redshift máximo (z-max)", value=0.3, min_value=0.0, max_value=10.0)
        
        radius = st.number_input("Radio de búsqueda [grados]", min_value=0.01, max_value=180.0, value=1.0, step=0.1, format="%.2f", help="Radio de búsqueda alrededor de las coordenadas RA/DEC")
        
        if st.button("🔍 Consultar SDSS", key="btn_sdss"):
            if not DB_AVAILABLE:
                st.error("❌ El módulo DB no está disponible. Verifique la instalación.")
                if base_error:
                    st.code(base_error, language='text')
            else:
                with st.spinner("Consultando base de datos SDSS..."):
                    try:
                        resultado = st.session_state.base_datos.conectar(
                            ra=ra, dec=dec, z_min=z_min, z_max=z_max, radius=radius, source="SDSS"
                        )
                    
                        if resultado is not None:
                            archivo_guardado = st.session_state.base_datos.guardardatos(resultado, "SDSS")
                            
                            if hasattr(resultado, 'to_pandas'):
                                st.session_state.datos_actuales = resultado.to_pandas()
                            else:
                                st.session_state.datos_actuales = resultado
                            
                            st.session_state.fuente_actual = "SDSS"
                            st.session_state.metadatos['archivo'] = archivo_guardado
                            
                            st.success(f"✅ Consulta exitosa: {len(st.session_state.datos_actuales)} objetos encontrados")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ No se obtuvieron resultados de la consulta")
                            
                    except Exception as e:
                        st.error(f"❌ Error en la consulta: {str(e)}")
                        st.code(str(e), language='text')
    
    # ===== DESI =====
    elif fuente == "DESI - Cosmos Profundo":
        st.subheader("🔭 DESI - Dark Energy Spectroscopic Instrument")
        st.write("Objetos del cosmos profundo para estudios de energía oscura")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ra = st.number_input("Right Ascension (RA) [grados]", value=180.0, min_value=0.0, max_value=360.0, key="desi_ra")
            dec = st.number_input("Declination (DEC) [grados]", value=0.0, min_value=-90.0, max_value=90.0, key="desi_dec")
        
        with col2:
            z_min = st.number_input("Redshift mínimo (z-min)", value=0.05, min_value=0.0, max_value=10.0, key="desi_zmin")
            z_max = st.number_input("Redshift máximo (z-max)", value=0.3, min_value=0.0, max_value=10.0, key="desi_zmax")
        
        radius = st.number_input("Radio de búsqueda [grados]", min_value=0.01, max_value=180.0, value=1.0, step=0.1, format="%.2f", key="desi_radius", help="Radio de búsqueda alrededor de las coordenadas RA/DEC")
        
        if st.button("🔍 Consultar DESI", key="btn_desi"):
            with st.spinner("Consultando base de datos DESI..."):
                try:
                    resultado = st.session_state.base_datos.conectar(
                        ra=ra, dec=dec, z_min=z_min, z_max=z_max, radius=radius, source="DESI"
                    )
                    
                    if resultado is not None:
                        archivo_guardado = st.session_state.base_datos.guardardatos(resultado, "DESI")
                        
                        if hasattr(resultado, 'to_pandas'):
                            st.session_state.datos_actuales = resultado.to_pandas()
                        else:
                            st.session_state.datos_actuales = resultado
                        
                        st.session_state.fuente_actual = "DESI"
                        st.session_state.metadatos['archivo'] = archivo_guardado
                        
                        st.success(f"✅ Consulta exitosa: {len(st.session_state.datos_actuales)} objetos encontrados")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ No se obtuvieron resultados de la consulta")
                        
                except Exception as e:
                    st.error(f"❌ Error en la consulta: {str(e)}")
    
    # ===== NASA ESI =====
    elif fuente == "NASA ESI - Exoplanetas":
        st.subheader("🪐 NASA ESI - Exoplanet Systems")
        st.write("Base de datos de exoplanetas y sistemas planetarios")
        
        st.info("Esta fuente no requiere parámetros adicionales")
        
        if st.button("🔍 Consultar NASA ESI", key="btn_nasa"):
            with st.spinner("Consultando base de datos NASA ESI..."):
                try:
                    resultado = st.session_state.base_datos.conectar(source="NASA ESI")
                    
                    if resultado is not None:
                        archivo_guardado = st.session_state.base_datos.guardardatos(resultado, "NASA_ESI")
                        
                        if hasattr(resultado, 'to_pandas'):
                            st.session_state.datos_actuales = resultado.to_pandas()
                        else:
                            st.session_state.datos_actuales = resultado
                        
                        st.session_state.fuente_actual = "NASA ESI"
                        st.session_state.metadatos['archivo'] = archivo_guardado
                        
                        st.success(f"✅ Consulta exitosa: {len(st.session_state.datos_actuales)} exoplanetas encontrados")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ No se obtuvieron resultados de la consulta")
                        
                except Exception as e:
                    st.error(f"❌ Error en la consulta: {str(e)}")
    
    # ===== NEO =====
    elif fuente == "NEO - Asteroides y Cometas":
        st.subheader("☄️ NEO - Near-Earth Objects")
        st.write("Asteroides y cometas cercanos a la Tierra")
        
        st.info("Esta fuente no requiere parámetros adicionales")
        
        if st.button("🔍 Consultar NEO", key="btn_neo"):
            with st.spinner("Consultando base de datos NEO..."):
                try:
                    resultado = st.session_state.base_datos.conectar(source="NEO")
                    
                    if resultado is not None:
                        archivo_guardado = st.session_state.base_datos.guardardatos(resultado, "NEO")
                        
                        if hasattr(resultado, 'to_pandas'):
                            st.session_state.datos_actuales = resultado.to_pandas()
                        else:
                            st.session_state.datos_actuales = resultado
                        
                        st.session_state.fuente_actual = "NEO"
                        st.session_state.metadatos['archivo'] = archivo_guardado
                        
                        st.success(f"✅ Consulta exitosa: {len(st.session_state.datos_actuales)} objetos encontrados")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ No se obtuvieron resultados de la consulta")
                        
                except Exception as e:
                    st.error(f"❌ Error en la consulta: {str(e)}")

# ==================== PÁGINA DE VER DATOS ====================
elif pagina == "📊 Ver Datos":
    if st.session_state.datos_actuales is None:
        st.warning("⚠️ No hay datos cargados. Por favor, cargue datos primero.")
    else:
        st.header("📊 Visualización de Datos")
        
        df = st.session_state.datos_actuales
        
        # Resumen
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Registros", len(df))
        with col2:
            st.metric("📋 Columnas", len(df.columns))
        with col3:
            st.metric("📂 Fuente", st.session_state.fuente_actual)
        
        st.markdown("---")
        
        # Tabs para diferentes vistas
        tab1, tab2, tab3 = st.tabs(["🔍 Vista de Datos", "📈 Estadísticas", "📊 Columnas"])
        
        with tab1:
            st.subheader("Primeras filas del dataset")
            n_rows = st.slider("Número de filas a mostrar:", 5, 50, 10)
            st.dataframe(df.head(n_rows), use_container_width=True)
            
            # Opción de descargar
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar datos (CSV)",
                data=csv,
                file_name=f"astroquipu_{st.session_state.fuente_actual}.csv",
                mime="text/csv"
            )
        
        with tab2:
            st.subheader("Estadísticas Descriptivas")
            st.dataframe(df.describe(), use_container_width=True)
            
            st.subheader("Información de tipos de datos")
            info_df = pd.DataFrame({
                'Columna': df.columns,
                'Tipo': df.dtypes.values,
                'Valores No Nulos': df.count().values,
                'Valores Nulos': df.isnull().sum().values
            })
            st.dataframe(info_df, use_container_width=True)
        
        with tab3:
            st.subheader("Lista de Columnas Disponibles")
            for i, col in enumerate(df.columns, 1):
                st.write(f"**{i}.** `{col}` - {df[col].dtype}")

# ==================== PÁGINA DE CÁLCULOS ====================
elif pagina == "🔬 Cálculos":
    if st.session_state.datos_actuales is None:
        st.warning("⚠️ No hay datos cargados. Por favor, cargue datos primero.")
    else:
        st.header("🔬 Cálculos Astronómicos")
        
        if not CALC_AVAILABLE:
            st.error("❌ El módulo de Cálculos no está disponible")
            if 'Calculations.Calculations' in import_errors:
                st.code(import_errors['Calculations.Calculations'], language='text')
        else:
            df = st.session_state.datos_actuales
            
            # Información del dataset
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📝 Registros", len(df))
            with col2:
                st.metric("📂 Fuente", st.session_state.fuente_actual)
            
            st.markdown("---")
            
            # Selector de tipo de cálculo
            tipo_calculo = st.selectbox(
                "Seleccione el tipo de cálculo:",
                ["Seleccione una opción...", 
                 "Calcular Constante de Hubble (H₀)",
                 "Calcular Redshift (z)",
                 "Calcular Distancia por Ley de Hubble"],
                key="selector_calculo"
            )
            
            # ===== CALCULAR CONSTANTE DE HUBBLE =====
            if tipo_calculo == "Calcular Constante de Hubble (H₀)":
                st.subheader("🌌 Calcular Constante de Hubble")
                st.write("Calcula H₀ = v/d para cada fila del dataset")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    col_velocidad = st.selectbox(
                        "Seleccione columna de velocidad (km/s):",
                        ["Seleccione..."] + list(df.select_dtypes(include=['float64', 'int64']).columns),
                        key="col_vel_hubble"
                    )
                
                with col2:
                    col_distancia = st.selectbox(
                        "Seleccione columna de distancia (Mpc):",
                        ["Seleccione..."] + list(df.select_dtypes(include=['float64', 'int64']).columns),
                        key="col_dist_hubble"
                    )
                
                if st.button("🚀 Calcular H₀", key="btn_calc_hubble"):
                    if col_velocidad != "Seleccione..." and col_distancia != "Seleccione...":
                        with st.spinner("Calculando..."):
                            try:
                                calculador = st.session_state.menu_calculos.calculador
                                
                                # Calcular H0 para cada fila
                                df['H0_calculado'] = df.apply(
                                    lambda row: calculador.calcularHubble(
                                        row[col_velocidad], 
                                        row[col_distancia]
                                    ),
                                    axis=1
                                )
                                
                                # Actualizar datos en session_state
                                st.session_state.datos_actuales = df
                                
                                st.success("✅ Cálculo completado! Nueva columna 'H0_calculado' añadida")
                                
                                # Mostrar estadísticas
                                st.write("### 📊 Estadísticas de H₀ calculado:")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Media", f"{df['H0_calculado'].mean():.2f} km/s/Mpc")
                                with col2:
                                    st.metric("Mediana", f"{df['H0_calculado'].median():.2f} km/s/Mpc")
                                with col3:
                                    st.metric("Desv. Std", f"{df['H0_calculado'].std():.2f}")
                                
                                # Mostrar resultados
                                st.write("### 📋 Primeros resultados:")
                                st.dataframe(df[[col_velocidad, col_distancia, 'H0_calculado']].head(10))
                                
                                # Gráfico
                                st.write("### 📈 Distribución de H₀:")
                                st.bar_chart(df['H0_calculado'].value_counts().sort_index())
                                
                            except Exception as e:
                                st.error(f"❌ Error durante el cálculo: {str(e)}")
                    else:
                        st.warning("⚠️ Por favor seleccione ambas columnas")
            
            # ===== CALCULAR REDSHIFT =====
            elif tipo_calculo == "Calcular Redshift (z)":
                st.subheader("🔴 Calcular Redshift")
                st.write("Calcula z = (λ_obs - λ_emit) / λ_emit")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    col_obs = st.selectbox(
                        "Seleccione columna de λ observada:",
                        ["Seleccione..."] + list(df.select_dtypes(include=['float64', 'int64']).columns),
                        key="col_lambda_obs"
                    )
                
                with col2:
                    col_emit = st.selectbox(
                        "Seleccione columna de λ emitida:",
                        ["Seleccione..."] + list(df.select_dtypes(include=['float64', 'int64']).columns),
                        key="col_lambda_emit"
                    )
                
                if st.button("🚀 Calcular Redshift", key="btn_calc_redshift"):
                    if col_obs != "Seleccione..." and col_emit != "Seleccione...":
                        with st.spinner("Calculando..."):
                            try:
                                calculador = st.session_state.menu_calculos.calculador
                                
                                # Calcular redshift para cada fila
                                df['redshift_calculado'] = df.apply(
                                    lambda row: calculador.calcularRedshift(
                                        row[col_obs], 
                                        row[col_emit]
                                    ),
                                    axis=1
                                )
                                
                                # Actualizar datos
                                st.session_state.datos_actuales = df
                                
                                st.success("✅ Cálculo completado! Nueva columna 'redshift_calculado' añadida")
                                
                                # Estadísticas
                                st.write("### 📊 Estadísticas de Redshift:")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Media", f"{df['redshift_calculado'].mean():.4f}")
                                with col2:
                                    st.metric("Mediana", f"{df['redshift_calculado'].median():.4f}")
                                with col3:
                                    st.metric("Desv. Std", f"{df['redshift_calculado'].std():.4f}")
                                
                                # Resultados
                                st.write("### 📋 Primeros resultados:")
                                st.dataframe(df[[col_obs, col_emit, 'redshift_calculado']].head(10))
                                
                                # Gráfico
                                st.write("### 📈 Distribución de Redshift:")
                                st.line_chart(df['redshift_calculado'])
                                
                            except Exception as e:
                                st.error(f"❌ Error durante el cálculo: {str(e)}")
                    else:
                        st.warning("⚠️ Por favor seleccione ambas columnas")
            
            # ===== CALCULAR DISTANCIA POR LEY DE HUBBLE =====
            elif tipo_calculo == "Calcular Distancia por Ley de Hubble":
                st.subheader("📏 Calcular Distancia por Ley de Hubble")
                st.write("Calcula distancia en Mpc usando d = c·z/H₀")
                
                col_redshift = st.selectbox(
                    "Seleccione columna de redshift (z):",
                    ["Seleccione..."] + list(df.select_dtypes(include=['float64', 'int64']).columns),
                    key="col_redshift_dist"
                )
                
                if st.button("🚀 Calcular Distancia", key="btn_calc_distancia"):
                    if col_redshift != "Seleccione...":
                        with st.spinner("Calculando..."):
                            try:
                                calculador = st.session_state.menu_calculos.calculador
                                
                                # Calcular distancia
                                df['distancia_Mpc_calculada'] = df[col_redshift].apply(
                                    calculador.calcularDistanciaHubble
                                )
                                
                                # Actualizar datos
                                st.session_state.datos_actuales = df
                                
                                st.success("✅ Cálculo completado! Nueva columna 'distancia_Mpc_calculada' añadida")
                                
                                # Estadísticas
                                st.write("### 📊 Estadísticas de Distancia:")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Media", f"{df['distancia_Mpc_calculada'].mean():.2f} Mpc")
                                with col2:
                                    st.metric("Mediana", f"{df['distancia_Mpc_calculada'].median():.2f} Mpc")
                                with col3:
                                    st.metric("Desv. Std", f"{df['distancia_Mpc_calculada'].std():.2f}")
                                
                                # Resultados
                                st.write("### 📋 Primeros resultados:")
                                st.dataframe(df[[col_redshift, 'distancia_Mpc_calculada']].head(10))
                                
                                # Gráfico
                                st.write("### 📈 Relación z vs Distancia:")
                                chart_data = df[[col_redshift, 'distancia_Mpc_calculada']].copy()
                                chart_data = chart_data.set_index(col_redshift)
                                st.line_chart(chart_data)
                                
                            except Exception as e:
                                st.error(f"❌ Error durante el cálculo: {str(e)}")
                    else:
                        st.warning("⚠️ Por favor seleccione una columna")

# ==================== PÁGINA DE MACHINE LEARNING ====================
elif pagina == "🤖 Machine Learning":
    if st.session_state.datos_actuales is None:
        st.warning("⚠️ No hay datos cargados. Por favor, cargue datos primero.")
    else:
        st.header("🤖 Machine Learning")
        st.info("Aquí se integrarán las herramientas de ML del módulo MenuML")
        
        # Llamar al módulo de ML
        try:
            st.write("### Módulo de Machine Learning")
            st.write("Datos disponibles para análisis:")
            st.write(f"- **Fuente:** {st.session_state.fuente_actual}")
            st.write(f"- **Registros:** {len(st.session_state.datos_actuales)}")
            
            # Aquí puedes integrar las funciones específicas de MenuML
            st.warning("🚧 Integración con MenuML en desarrollo")
            
        except Exception as e:
            st.error(f"Error al cargar el módulo de ML: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🌌 AstroQuipu - Sistema de Análisis Astronómico Educativo</p>
        <p style='font-size: 0.8em; color: gray;'>Desarrollado con ❤️ para la astronomía</p>
    </div>
    """,
    unsafe_allow_html=True
)
