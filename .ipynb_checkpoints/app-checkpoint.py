import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path
import sys
import os

# Configuración de la página
st.set_page_config(
    page_title="AstroPhysics Portal",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Agregar la ruta de Calculations al path
calculations_path = Path(__file__).parent / "Calculations"
sys.path.append(str(calculations_path))

# Función para convertir el GIF a base64
def load_reloj_gif():
    try:
        gif_path = Path("static/images/reloj.gif")
        if gif_path.exists():
            with open(gif_path, "rb") as f:
                data = f.read()
            data_url = "data:image/gif;base64," + base64.b64encode(data).decode()
            return data_url
        else:
            st.error(f"Archivo no encontrado: {gif_path}")
            return None
    except Exception as e:
        st.error(f"Error cargando el GIF: {e}")
        return None

# Cargar el GIF
gif_data_url = load_reloj_gif()

# CSS para ocultar elementos de Streamlit
st.markdown("""
<style>
    #MainMenu, footer, header, .stApp > header { 
        display: none !important; 
    }
    
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        background: transparent !important;
    }
    
    .stApp {
        background: transparent !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    iframe {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
        z-index: 9999 !important;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'orbital'

# Verificar parámetros de URL para navegación
query_params = st.experimental_get_query_params()
if 'page' in query_params:
    st.session_state.current_page = query_params['page'][0]
    # Limpiar parámetros
    st.experimental_set_query_params()

# Función para cargar el HTML dinámicamente CON EL GIF
def load_orbital_interface():
    # Si tenemos el GIF, usarlo, sino usar un emoji como fallback
    if gif_data_url:
        clock_content = f'<img src="{gif_data_url}" alt="Reloj" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">'
    else:
        clock_content = '<div style="width: 100%; height: 100%; border-radius: 50%; background: radial-gradient(circle, #00e5ff, #0077ff); display: flex; align-items: center; justify-content: center; color: white; font-size: 48px;">🌌</div>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --space-dark: #0a0e17;
                --space-blue: #1a2b47;
                --accent: #00e5ff;
                --text: #e0f7fa;
            }}

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                background: radial-gradient(circle at center, #000 0%, #001017 70%, #002024 100%);
                color: var(--text);
                font-family: 'Outfit', sans-serif;
                overflow: hidden;
                height: 100vh;
                width: 100vw;
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
            }}

            /* ✨ Luz ambiental */
            body::before {{
                content: "";
                position: fixed;
                width: 200vw;
                height: 200vh;
                border-radius: 70%;
                background: radial-gradient(circle, rgba(0,255,255,0) 40%, rgba(0,150,255,0.15) 30%, rgba(0,255,255,0.25) 100%);
                filter: blur(120px);
                z-index: 0;
                animation: ambientShift 8s infinite ease-in-out;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
            }}

            @keyframes ambientShift {{
                0%, 100% {{ opacity: 0.3; transform: translate(-50%, -50%) scale(1); }}
                50% {{ opacity: 0.8; transform: translate(-50%, -50%) scale(1.1); }}
            }}

            /* 🛰️ Barra superior */
            nav {{
                position: fixed;
                top: 0;
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 1rem 3rem;
                background: rgba(10, 14, 23, 0.45);
                backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(0, 229, 255, 0.1);
                z-index: 10;
            }}

            .nav-logo {{
                display: flex;
                align-items: center;
                gap: 1rem;
                font-weight: 500;
                font-size: 1.4rem;
                color: var(--text);
                letter-spacing: 1px;
                cursor: pointer;
                transition: color 0.3s ease;
            }}

            .nav-logo:hover {{ color: var(--accent); }}

            .nav-links {{
                display: flex;
                gap: 2.5rem;
            }}

            .nav-links a {{
                color: var(--text);
                text-decoration: none;
                font-size: 1.1rem;
                letter-spacing: 1px;
                position: relative;
                transition: color 0.3s ease;
            }}

            .nav-links a::before,
            .nav-links a::after {{
                content: "";
                position: absolute;
                width: 0;
                height: 1px;
                bottom: -3px;
                background: var(--accent);
                transition: width 0.3s ease;
                opacity: 0.6;
            }}

            .nav-links a::before {{ left: 50%; }}
            .nav-links a::after {{ right: 50%; }}

            .nav-links a:hover {{
                color: var(--accent);
            }}

            .nav-links a:hover::before,
            .nav-links a:hover::after {{
                width: 50%;
            }}

            .nav-action button {{
                background: transparent;
                border: 1px solid var(--accent);
                color: var(--accent);
                padding: 0.6rem 1.5rem;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1rem;
                letter-spacing: 0.5px;
                transition: all 0.3s ease;
            }}

            .nav-action button:hover {{
                background: var(--accent);
                color: var(--space-dark);
                box-shadow: 0 0 15px var(--accent);
            }}

            /* 🌌 Contenedor central */
            .container {{
                position: relative;
                width: 1200px;
                height: 800px;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 2;
            }}

            /* 🪐 Reloj */
            .clock-container {{
                position: absolute;
                z-index: 3;
                width: 150px;
                height: 150px;
                cursor: pointer;
                transition: transform 0.3s ease;
                border-radius: 50%;
                overflow: hidden;
            }}

            .clock-container:hover {{ transform: scale(1.05); }}

            .clock-content {{
                width: 100%;
                height: 100%;
                border-radius: 0%;
                transition: transform 0.1s ease-out;
            }}

            /* ✨ Menú orbital */
            .menu {{
                position: absolute;
                width: 100%;
                height: 100%;
                z-index: 2;
                display: flex;
                justify-content: space-between;
            }}

            .menu-column {{
                display: flex;
                flex-direction: column;
                justify-content: center;
                gap: 150px;
                width: 280px;
            }}

            .menu-column.left {{ align-items: flex-end; }}
            .menu-column.right {{ align-items: flex-start; }}

            .menu button {{
                background: transparent;
                color: var(--text);
                border: none;
                font-size: 1.3rem;
                cursor: pointer;
                padding: 1.5rem 2rem;
                letter-spacing: 2px;
                text-transform: uppercase;
                transition: color 0.3s ease;
                outline: none;
                width: 260px;
                position: relative;
                z-index: 4;
            }}

            .menu button:hover {{ color: var(--accent); }}

            .menu button::before,
            .menu button::after {{
                content: "";
                position: absolute;
                width: 0;
                height: 0;
                border: 2px solid var(--accent);
                opacity: 0;
                transition: all 0.4s ease;
            }}

            .menu button::before {{
                top: 0; left: 0;
                border-right: none; border-bottom: none;
            }}

            .menu button::after {{
                bottom: 0; right: 0;
                border-left: none; border-top: none;
            }}

            .menu button:hover::before,
            .menu button:hover::after {{
                width: 100%;
                height: 100%;
                opacity: 1;
            }}

            /* ⚡ Líneas precisas */
            .connection-line {{
                position: absolute;
                background: var(--accent);
                height: 3px;
                width: 0;
                z-index: 1;
                opacity: 0;
                box-shadow: 0 0 15px var(--accent);
                transition: all 0.5s ease;
                pointer-events: none;
                transform-origin: left center;
            }}

            .line-active {{
                opacity: 1 !important;
                width: var(--line-width, 300px) !important;
            }}

            #line-analisis {{
                top: 200px;
                left: 600px;
                transform: rotate(150deg);
                --line-width: 300px;
            }}

            #line-mis-analisis {{
                top: 500px;
                left: 600px;
                transform: rotate(210deg);
                --line-width: 300px;
            }}

            #line-aprende {{
                top: 200px;
                left: 600px;
                transform: rotate(30deg);
                --line-width: 300px;
            }}

            #line-simula {{
                top: 500px;
                left: 600px;
                transform: rotate(-30deg);
                --line-width: 300px;
            }}
        </style>
    </head>
    <body>
        <!-- 🛰️ Barra superior -->
        <nav>
            <div class="nav-logo">
                <span style="font-size: 1.8rem;">🌌</span>
                AstroQuipu
            </div>

            <div class="nav-links">
                <a href="?page=descripcion" id="nav-descripcion">Descripción</a>
                <a href="?page=funciones" id="nav-funciones">Funciones</a>
                <a href="?page=analisis" id="nav-calculo">Cálculo</a>
                <a href="?page=simula" id="nav-simula">Simula</a>
                <a href="?page=aprende" id="nav-aprende">Aprende</a>
            </div>

            <div class="nav-action">
                <a href="?page=perfil" style="text-decoration: none;">
                    <button id="nav-perfil">Mi Perfil</button>
                </a>
            </div>
        </nav>

        <!-- 🌠 Interfaz orbital -->
        <div class="container">
            <div class="clock-container" id="clock">
                <div class="clock-content">
                    {clock_content}
                </div>
            </div>

            <div class="menu">
                <div class="menu-column left">
                    <a href="?page=analisis" style="text-decoration: none;">
                        <button id="btn-analisis" data-line="line-analisis">Cálculo de Datos</button>
                    </a>
                    <a href="?page=mis_analisis" style="text-decoration: none;">
                        <button id="btn-mis-analisis" data-line="line-mis-analisis">Mis Análisis</button>
                    </a>
                </div>
                <div class="menu-column right">
                    <a href="?page=aprende" style="text-decoration: none;">
                        <button id="btn-aprende" data-line="line-aprende">Aprende del Universo</button>
                    </a>
                    <a href="?page=simula" style="text-decoration: none;">
                        <button id="btn-simula" data-line="line-simula">Simula el Universo</button>
                    </a>
                </div>
            </div>

            <!-- 🔗 Líneas dinámicas -->
            <div class="connection-line" id="line-analisis"></div>
            <div class="connection-line" id="line-mis-analisis"></div>
            <div class="connection-line" id="line-aprende"></div>
            <div class="connection-line" id="line-simula"></div>
        </div>

        <script>
            // 🌀 Movimiento del reloj
            const clock = document.getElementById("clock");
            const clockContent = clock.querySelector(".clock-content");

            document.addEventListener("mousemove", (e) => {{
                const rect = clock.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                const deltaX = (e.clientX - centerX) / 30;
                const deltaY = (e.clientY - centerY) / 30;
                clockContent.style.transform = `translate(${{deltaX}}px, ${{deltaY}}px)`;
            }});

            document.addEventListener("mouseleave", () => {{
                clockContent.style.transform = "translate(0,0)";
            }});

            // ⚡ Líneas dinámicas
            const buttons = document.querySelectorAll('.menu button');
            const lines = document.querySelectorAll('.connection-line');

            buttons.forEach(btn => {{
                const line = document.getElementById(btn.dataset.line);
                
                btn.addEventListener('mouseenter', () => {{
                    lines.forEach(l => l.classList.remove('line-active'));
                    line.classList.add('line-active');
                }});
                
                btn.addEventListener('mouseleave', () => {{
                    setTimeout(() => line.classList.remove('line-active'), 150);
                }});
            }});

            // Prevenir comportamiento por defecto de los enlaces para mantener efectos visuales
            document.querySelectorAll('a').forEach(link => {{
                link.addEventListener('click', (e) => {{
                    // Los efectos visuales se mantienen, la navegación se hace por el href
                    console.log('Navegando a:', link.getAttribute('href'));
                }});
            }});
        </script>
    </body>
    </html>
    """
    return html_content

# CONTENIDO PRINCIPAL - ESTA ES LA ESTRUCTURA CORRECTA
if st.session_state.current_page == 'orbital':
    # Inyectar el HTML directamente
    components.html(load_orbital_interface(), height=800, scrolling=False)
    
elif st.session_state.current_page == 'analisis':
    # PÁGINA DE CÁLCULOS ASTRONÓMICOS
    st.markdown("""
    <style>
    .space-page {
        margin-top: 80px;
        padding: 2rem;
        color: white;
        min-height: 100vh;
        background: radial-gradient(circle at center, #000 0%, #001017 70%, #002024 100%);
        font-family: 'Outfit', sans-serif;
    }
    .space-title {
        color: #00e5ff;
        text-shadow: 0 0 10px #00e5ff;
        margin-bottom: 2rem;
    }
    .calculation-container {
        background: rgba(10, 14, 23, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        color: #e0f7fa;
    }
    .calculation-title {
        color: #00e5ff;
        text-shadow: 0 0 10px #00e5ff;
        border-bottom: 2px solid #00e5ff;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .result-box {
        background: rgba(0, 229, 255, 0.1);
        border: 1px solid #00e5ff;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .back-button {
        background: transparent;
        border: 1px solid #00e5ff;
        color: #00e5ff;
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Outfit', sans-serif;
    }
    .back-button:hover {
        background: #00e5ff;
        color: #0a0e17;
        box-shadow: 0 0 15px #00e5ff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="space-page">', unsafe_allow_html=True)
    st.markdown('<h1 class="space-title">🛰️ Laboratorio de Cálculos Astronómicos</h1>', unsafe_allow_html=True)
    
    # Tabs para diferentes tipos de cálculos
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌌 Constante de Hubble", 
        "🔴 Redshift", 
        "🔄 Velocidad Angular", 
        "🪐 Órbitas", 
        "📊 Datos CSV"
    ])
    
    # Try-except para importar los cálculos
    try:
        from calculos import Calculos
        calc = Calculos()
        
        with tab1:
            st.markdown('<div class="calculation-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="calculation-title">Cálculo de la Constante de Hubble</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                velocidad = st.number_input(
                    "Velocidad de recesión (km/s)", 
                    min_value=0.0, 
                    value=1500.0,
                    key="hubble_vel"
                )
            with col2:
                distancia = st.number_input(
                    "Distancia (Mpc)", 
                    min_value=0.1, 
                    value=22.0,
                    key="hubble_dist"
                )
            
            if st.button("Calcular H₀", key="calc_hubble"):
                try:
                    H = calc.calcularHubble(velocidad, distancia)
                    st.markdown(f"""
                    <div class="result-box">
                        <h4>📈 Resultado:</h4>
                        <p><strong>Velocidad:</strong> {velocidad:,.1f} km/s</p>
                        <p><strong>Distancia:</strong> {distancia:,.1f} Mpc</p>
                        <p><strong>Constante de Hubble:</strong> H₀ = {H:.2f} km/s/Mpc</p>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error en el cálculo: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="calculation-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="calculation-title">Cálculo del Redshift</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                long_obs = st.number_input(
                    "Longitud de onda observada (nm)", 
                    min_value=0.0, 
                    value=658.0,
                    key="redshift_obs"
                )
            with col2:
                long_emit = st.number_input(
                    "Longitud de onda emitida (nm)", 
                    min_value=0.1, 
                    value=656.3,
                    key="redshift_emit"
                )
            
            if st.button("Calcular Redshift", key="calc_redshift"):
                try:
                    z = calc.calcularRedshift(long_obs, long_emit)
                    velocidad_c = z * calc.c
                    st.markdown(f"""
                    <div class="result-box">
                        <h4>🔴 Resultado:</h4>
                        <p><strong>Longitud observada:</strong> {long_obs} nm</p>
                        <p><strong>Longitud emitida:</strong> {long_emit} nm</p>
                        <p><strong>Redshift:</strong> z = {z:.6f}</p>
                        <p><strong>Velocidad de recesión:</strong> {velocidad_c:.2f} km/s</p>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error en el cálculo: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="calculation-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="calculation-title">Cálculo de Velocidad Angular</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                v_lineal = st.number_input(
                    "Velocidad lineal (km/s)", 
                    min_value=0.0, 
                    value=220.0,
                    key="angular_vel"
                )
            with col2:
                radio = st.number_input(
                    "Radio de la órbita (km)", 
                    min_value=0.1, 
                    value=2.46e17,
                    key="angular_radio"
                )
            
            if st.button("Calcular Velocidad Angular", key="calc_angular"):
                try:
                    omega = calc.calcularVelocidadAngular(v_lineal, radio)
                    periodo_anos = (2 * 3.14159 / omega) / (365.25 * 24 * 3600)
                    st.markdown(f"""
                    <div class="result-box">
                        <h4>🔄 Resultado:</h4>
                        <p><strong>Velocidad lineal:</strong> {v_lineal:,.1f} km/s</p>
                        <p><strong>Radio orbital:</strong> {radio:.2e} km</p>
                        <p><strong>Velocidad angular:</strong> ω = {omega:.3e} rad/s</p>
                        <p><strong>Período orbital:</strong> ~{periodo_anos:.1f} millones de años</p>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error en el cálculo: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab4:
            st.markdown('<div class="calculation-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="calculation-title">Cálculo de Parámetros Orbitales</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                masa = st.number_input(
                    "Masa del objeto central (kg)", 
                    min_value=0.0, 
                    value=5.972e24,
                    key="orbita_masa"
                )
            with col2:
                radio_orb = st.number_input(
                    "Radio de la órbita (m)", 
                    min_value=0.1, 
                    value=6771000.0,
                    key="orbita_radio"
                )
            
            if st.button("Calcular Órbita", key="calc_orbita"):
                try:
                    v_orbital, periodo = calc.calcularOrbita(masa, radio_orb)
                    st.markdown(f"""
                    <div class="result-box">
                        <h4>🪐 Resultado:</h4>
                        <p><strong>Masa central:</strong> {masa:.3e} kg</p>
                        <p><strong>Radio orbital:</strong> {radio_orb/1000:,.0f} km</p>
                        <p><strong>Velocidad orbital:</strong> {v_orbital/1000:.2f} km/s</p>
                        <p><strong>Período orbital:</strong> {periodo/3600:.2f} horas</p>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error en el cálculo: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab5:
            st.markdown('<div class="calculation-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="calculation-title">Análisis de Datos CSV</h3>', unsafe_allow_html=True)
            
            # Verificar si existe el archivo CSV
            csv_path = calculations_path / "datos_galaxias.csv"
            if csv_path.exists():
                if st.button("Analizar Datos de Galaxias", key="analyze_csv"):
                    try:
                        resultados = calc.analizar_datos_csv(str(csv_path))
                        
                        st.markdown(f"""
                        <div class="result-box">
                            <h4>📊 Resultados del Análisis</h4>
                            <p><strong>Galaxias analizadas:</strong> {len(resultados)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Mostrar tabla de resultados
                        st.dataframe(resultados, use_container_width=True)
                        
                        # Estadísticas
                        H0_promedio = resultados['H0_calculado'].mean()
                        st.markdown(f"""
                        <div class="result-box">
                            <h4>📈 Estadísticas</h4>
                            <p><strong>Constante de Hubble promedio:</strong> H₀ = {H0_promedio:.2f} km/s/Mpc</p>
                            <p><strong>Desviación estándar:</strong> ±{resultados['H0_calculado'].std():.2f} km/s/Mpc</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Error al analizar el CSV: {e}")
            else:
                st.warning("""
                **Archivo no encontrado:** `Calculations/datos_galaxias.csv`
                
                Crea un archivo CSV con las siguientes columnas:
                - `galaxia`: Nombre de la galaxia
                - `velocidad`: Velocidad en km/s  
                - `distancia`: Distancia en Mpc
                - `longitud_obs`: Longitud observada (opcional)
                - `longitud_emit`: Longitud emitida (opcional)
                """)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    except ImportError as e:
        st.error(f"""
        **Error al importar los módulos de cálculo:**
        
        Asegúrate de que la estructura de carpetas sea:
        ```
        tu_proyecto/
        ├── app.py
        ├── Calculations/
        │   ├── calculos.py
        │   ├── datos_galaxias.csv
        │   └── __init__.py
        ```
        
        Error detallado: {e}
        """)
    
    # Botón para volver
    if st.button("← Volver al Portal Principal", key="back_from_calc"):
        st.session_state.current_page = 'orbital'
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# OTRAS PÁGINAS (simula, aprende, perfil, etc.)
elif st.session_state.current_page == 'mis_analisis':
    st.markdown('<div class="space-page">', unsafe_allow_html=True)
    st.markdown('<h1 class="space-title">📁 Mis Análisis</h1>', unsafe_allow_html=True)
    st.write("Tus análisis guardados y resultados anteriores")
    if st.button("← Volver al Portal Principal"):
        st.session_state.current_page = 'orbital'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
elif st.session_state.current_page == 'aprende':
    st.markdown('<div class="space-page">', unsafe_allow_html=True)
    st.markdown('<h1 class="space-title">🎓 Aprende del Universo</h1>', unsafe_allow_html=True)
    st.write("Contenido educativo sobre astronomía y astrofísica")
    if st.button("← Volver al Portal Principal"):
        st.session_state.current_page = 'orbital'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
elif st.session_state.current_page == 'simula':
    st.markdown('<div class="space-page">', unsafe_allow_html=True)
    st.markdown('<h1 class="space-title">🌠 Simula el Universo</h1>', unsafe_allow_html=True)
    st.write("Simulaciones interactivas de fenómenos astronómicos")
    if st.button("← Volver al Portal Principal"):
        st.session_state.current_page = 'orbital'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
elif st.session_state.current_page == 'perfil':
    st.markdown('<div class="space-page">', unsafe_allow_html=True)
    st.markdown('<h1 class="space-title">👤 Mi Perfil</h1>', unsafe_allow_html=True)
    st.write("Gestión de tu cuenta y preferencias")
    if st.button("← Volver al Portal Principal"):
        st.session_state.current_page = 'orbital'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
elif st.session_state.current_page == 'descripcion':
    st.markdown('<div class="space-page">', unsafe_allow_html=True)
    st.markdown('<h1 class="space-title">📖 Descripción</h1>', unsafe_allow_html=True)
    st.write("Información sobre AstroQuipu")
    if st.button("← Volver al Portal Principal"):
        st.session_state.current_page = 'orbital'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
elif st.session_state.current_page == 'funciones':
    st.markdown('<div class="space-page">', unsafe_allow_html=True)
    st.markdown('<h1 class="space-title">⚙️ Funciones</h1>', unsafe_allow_html=True)
    st.write("Funcionalidades de la plataforma")
    if st.button("← Volver al Portal Principal"):
        st.session_state.current_page = 'orbital'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)