import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path
import sys
import os
import pandas as pd
import json
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="AstroQuipu - Portal Astronómico",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Agregar la ruta de Calculations al path
calculations_path = Path(__file__).parent / "Calculations"
sys.path.append(str(calculations_path))

# Importar la clase Calculos
try:
    from calculos import Calculos
    calc = Calculos()
except ImportError as e:
    class Calculos:
        def __init__(self):
            self.c = 299792.458
            self.H0 = 70
            self.G = 6.674e-11
        
        def calcularHubble(self, velocidad, distancia):
            return velocidad / distancia if distancia != 0 else 0
        
        def calcularRedshift(self, longitud_observada, longitud_emitida):
            return (longitud_observada - longitud_emitida) / longitud_emitida if longitud_emitida != 0 else 0
        
        def calcularVelocidadAngular(self, velocidad_lineal, radio):
            return (velocidad_lineal * 1000) / (radio * 1000) if radio != 0 else 0
        
        def calcularOrbita(self, masa_central, radio):
            v_orbital = np.sqrt(self.G * masa_central / radio) if radio > 0 and masa_central > 0 else 0
            periodo = 2 * np.pi * radio / v_orbital if v_orbital > 0 else 0
            return v_orbital, periodo
        
        def calcularDistanciaHubble(self, redshift):
            return (self.c * redshift) / self.H0
        
        def analizar_datos_csv(self, archivo_csv):
            try:
                df = pd.read_csv(archivo_csv)
                resultados = []
                for idx, row in df.iterrows():
                    resultado = {
                        'galaxia': row['galaxia'],
                        'velocidad_km_s': row['velocidad'],
                        'distancia_Mpc': row['distancia']
                    }
                    resultado['H0_calculado'] = self.calcularHubble(row['velocidad'], row['distancia'])
                    if 'longitud_obs' in row and 'longitud_emit' in row:
                        resultado['redshift'] = self.calcularRedshift(row['longitud_obs'], row['longitud_emit'])
                        resultado['distancia_via_redshift'] = self.calcularDistanciaHubble(resultado['redshift'])
                    resultados.append(resultado)
                return pd.DataFrame(resultados)
            except Exception as e:
                return pd.DataFrame()
    calc = Calculos()

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
            return None
    except Exception as e:
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
        padding: 0px !important;
        max-width: 100% !important;
        background: transparent !important;
        margin: 0px !important;
        width: 100vw !important;
        height: 100vh !important;
    }
    
    .stApp {
        background: transparent !important;
        margin: 0px !important;
        padding: 0px !important;
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
    }
    
    section.main {
        padding: 0px !important;
        margin: 0px !important;
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    
    iframe {
        width: 100vw !important;
        height: 100vh !important;
        border: none !important;
        margin: 0px !important;
        padding: 0px !important;
        display: block !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
    }
    
    div[data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }
    
    body {
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado de la aplicación
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'orbital'
if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Verificar parámetros de URL para navegación
query_params = st.experimental_get_query_params()
if 'page' in query_params:
    st.session_state.current_page = query_params['page'][0]
    st.experimental_set_query_params()

# Función para cargar datos del CSV
def load_galaxy_data():
    try:
        csv_path = calculations_path / "datos_galaxias.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            return df.to_dict('records')
        else:
            return [
                {"galaxia": "Andrómeda", "velocidad": 301, "distancia": 0.77, "longitud_obs": 656.8, "longitud_emit": 656.3},
                {"galaxia": "Triángulo", "velocidad": 179, "distancia": 0.91, "longitud_obs": 656.5, "longitud_emit": 656.3},
                {"galaxia": "Centaurus A", "velocidad": 547, "distancia": 3.7, "longitud_obs": 657.2, "longitud_emit": 656.3},
                {"galaxia": "Sombrero", "velocidad": 872, "distancia": 9.55, "longitud_obs": 657.8, "longitud_emit": 656.3},
                {"galaxia": "Remolino", "velocidad": 463, "distancia": 7.27, "longitud_obs": 656.9, "longitud_emit": 656.3}
            ]
    except Exception as e:
        return []

def analyze_csv_data():
    try:
        csv_path = calculations_path / "datos_galaxias.csv"
        if csv_path.exists():
            analysis_df = calc.analizar_datos_csv(str(csv_path))
            return analysis_df.to_dict('records')
        else:
            results = []
            for galaxia in st.session_state.csv_data:
                H0 = calc.calcularHubble(galaxia['velocidad'], galaxia['distancia'])
                redshift = None
                distancia_redshift = None
                if 'longitud_obs' in galaxia and 'longitud_emit' in galaxia:
                    redshift = calc.calcularRedshift(galaxia['longitud_obs'], galaxia['longitud_emit'])
                    distancia_redshift = calc.calcularDistanciaHubble(redshift)
                
                results.append({
                    'galaxia': galaxia['galaxia'],
                    'velocidad_km_s': galaxia['velocidad'],
                    'distancia_Mpc': galaxia['distancia'],
                    'H0_calculado': H0,
                    'redshift': redshift,
                    'distancia_via_redshift': distancia_redshift
                })
            return results
    except Exception as e:
        return []

# ============================================
# PÁGINA ORBITAL (MENÚ PRINCIPAL)
# ============================================
def load_orbital_interface():
    # GIF sin cortarse - quitar border-radius del contenedor
    if gif_data_url:
        clock_content = f'<img src="{gif_data_url}" alt="Reloj" style="width: 100%; height: 100%; object-fit: contain;">'
    else:
        clock_content = '<div style="width: 100%; height: 100%; background: radial-gradient(circle, #00e5ff, #0077ff); display: flex; align-items: center; justify-content: center; color: white; font-size: 48px;">🌌</div>'
    
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

            html, body {{
                width: 100vw;
                height: 100vh;
                overflow: hidden;
            }}

            body {{
                background: radial-gradient(circle at center, #000 0%, #001017 70%, #002024 100%);
                color: var(--text);
                font-family: 'Outfit', sans-serif;
                overflow: hidden;
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
            }}

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

            .container {{
                position: relative;
                width: 1200px;
                height: 800px;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 2;
            }}

            .clock-container {{
                position: absolute;
                z-index: 3;
                width: 150px;
                height: 150px;
                cursor: pointer;
                transition: transform 0.3s ease;
                /* SIN border-radius para que el GIF no se corte */
            }}

            .clock-container:hover {{ transform: scale(1.05); }}

            .clock-content {{
                width: 100%;
                height: 100%;
                transition: transform 0.1s ease-out;
            }}

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
        <nav>
            <div class="nav-logo">
                <span style="font-size: 1.8rem;">◉</span>
                AstroQuipu
            </div>

            <div class="nav-links">
                <a href="?page=descripcion">Descripción</a>
                <a href="?page=funciones">Funciones</a>
                <a href="?page=analisis">Cálculo</a>
                <a href="?page=simula">Simula</a>
                <a href="?page=aprende">Aprende</a>
            </div>

            <div class="nav-action">
                <a href="?page=perfil" style="text-decoration: none;">
                    <button>Mi Perfil</button>
                </a>
            </div>
        </nav>

        <div class="container">
            <div class="clock-container" id="clock">
                <div class="clock-content">
                    {clock_content}
                </div>
            </div>

            <div class="menu">
                <div class="menu-column left">
                    <a href="?page=analisis" style="text-decoration: none;">
                        <button data-line="line-analisis">Cálculo de Datos</button>
                    </a>
                    <a href="?page=mis_analisis" style="text-decoration: none;">
                        <button data-line="line-mis-analisis">Mis Análisis</button>
                    </a>
                </div>
                <div class="menu-column right">
                    <a href="?page=aprende" style="text-decoration: none;">
                        <button data-line="line-aprende">Aprende del Universo</button>
                    </a>
                    <a href="?page=simula" style="text-decoration: none;">
                        <button data-line="line-simula">Simula el Universo</button>
                    </a>
                </div>
            </div>

            <div class="connection-line" id="line-analisis"></div>
            <div class="connection-line" id="line-mis-analisis"></div>
            <div class="connection-line" id="line-aprende"></div>
            <div class="connection-line" id="line-simula"></div>
        </div>

        <script>
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

            const buttons = document.querySelectorAll('.menu button');
            const lines = document.querySelectorAll('.connection-line');

            buttons.forEach(btn => {{
                const line = document.getElementById(btn.dataset.line);
                
                btn.addEventListener('mouseenter', () => {{
                    lines.forEach(l => l.classList.remove('line-active'));
                    if (line) line.classList.add('line-active');
                }});
                
                btn.addEventListener('mouseleave', () => {{
                    setTimeout(() => {{
                        if (line) line.classList.remove('line-active');
                    }}, 150);
                }});
            }});
        </script>
    </body>
    </html>
    """
    return html_content

# ============================================
# PÁGINA DE ANÁLISIS (Dashboard completo - igual que antes pero sin el resto del código aquí por límite de espacio)
# ============================================
def load_dashboard_html():
    # Cargar datos
    if st.session_state.csv_data is None:
        st.session_state.csv_data = load_galaxy_data()
    
    if st.session_state.analysis_results is None and st.session_state.csv_data:
        st.session_state.analysis_results = analyze_csv_data()
    
    csv_data_json = json.dumps(st.session_state.csv_data) if st.session_state.csv_data else "[]"
    analysis_results_json = json.dumps(st.session_state.analysis_results) if st.session_state.analysis_results else "[]"
    
    # Aquí va TODO el HTML del dashboard que te pasé antes
    # Por brevedad, solo indico que uses el HTML completo del dashboard anterior
    html_content = f"""


     <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AstroQuipu - Dashboard de Análisis</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --space-dark: #0a0e17;
                --space-blue: #1a2b47;
                --accent: #00e5ff;
                --text: #e0f7fa;
                --border: rgba(0, 229, 255, 0.2);
                --sidebar-bg: rgba(10, 14, 23, 0.9);
                --card-bg: rgba(26, 43, 71, 0.6);
                --hover-bg: rgba(0, 229, 255, 0.1);
            }}

            * {{ margin: 0; padding: 0; box-sizing: border-box; }}

            html, body {{ width: 100%; height: 100%; overflow: hidden; }}

            body {{
                background: radial-gradient(circle at center, #000 0%, #001017 70%, #002024 100%);
                color: var(--text);
                font-family: 'Outfit', sans-serif;
                overflow: hidden;
            }}

            body::before {{
                content: "";
                position: fixed;
                width: 200%;
                height: 200%;
                border-radius: 70%;
                background: radial-gradient(circle, rgba(0,255,255,0) 40%, rgba(0,150,255,0.15) 30%, rgba(0,255,255,0.25) 100%);
                filter: blur(120px);
                z-index: -1;
                animation: ambientShift 8s infinite ease-in-out;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
            }}

            @keyframes ambientShift {{
                0%, 100% {{ opacity: 0.3; transform: translate(-50%, -50%) scale(1); }}
                50% {{ opacity: 0.8; transform: translate(-50%, -50%) scale(1.1); }}
            }}

            .navbar {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0.8rem 1.5rem;
                background: rgba(10, 14, 23, 0.85);
                backdrop-filter: blur(10px);
                border-bottom: 1px solid var(--border);
                position: sticky;
                top: 0;
                z-index: 100;
                width: 100%;
            }}

            .navbar-left {{ display: flex; align-items: center; gap: 1rem; }}

            .navbar-logo {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-weight: 600;
                font-size: 1.2rem;
                color: var(--text);
                cursor: pointer;
                transition: color 0.3s ease;
            }}

            .navbar-logo:hover {{ color: var(--accent); }}

            .navbar-search {{ position: relative; width: 300px; }}

            .navbar-search input {{
                width: 100%;
                padding: 0.5rem 1rem 0.5rem 2.5rem;
                background: rgba(26, 43, 71, 0.6);
                border: 1px solid var(--border);
                border-radius: 6px;
                color: var(--text);
                font-family: 'Outfit', sans-serif;
                font-size: 0.9rem;
                transition: all 0.3s ease;
            }}

            .navbar-search input:focus {{
                outline: none;
                border-color: var(--accent);
                box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.2);
            }}

            .navbar-search::before {{
                content: "○";
                position: absolute;
                left: 0.8rem;
                top: 50%;
                transform: translateY(-50%);
                font-size: 0.9rem;
                color: var(--text);
                opacity: 0.7;
            }}

            .navbar-right {{ display: flex; align-items: center; gap: 1rem; }}

            .navbar-button {{
                background: transparent;
                border: 1px solid var(--border);
                color: var(--text);
                padding: 0.5rem 1rem;
                border-radius: 6px;
                cursor: pointer;
                font-family: 'Outfit', sans-serif;
                font-size: 0.9rem;
                transition: all 0.3s ease;
            }}

            .navbar-button:hover {{
                background: var(--hover-bg);
                border-color: var(--accent);
            }}

            .navbar-avatar {{
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--accent), #0077ff);
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--space-dark);
                font-weight: bold;
                cursor: pointer;
            }}

            .dashboard-container {{
                display: flex;
                width: 100%;
                height: calc(100vh - 70px);
                margin: 0;
                padding: 0;
                gap: 0;
                overflow: hidden;
            }}

            .sidebar {{
                width: 260px;
                flex-shrink: 0;
                background: var(--sidebar-bg);
                border-right: 1px solid var(--border);
                overflow: hidden;
                backdrop-filter: blur(10px);
                height: 100%;
                overflow-y: auto;
            }}

            .sidebar-header {{
                padding: 1.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .sidebar-title {{
                font-size: 1.1rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }}

            .sidebar-subtitle {{
                font-size: 0.85rem;
                opacity: 0.7;
            }}

            .sidebar-menu {{
                padding: 1rem 0;
            }}

            .sidebar-item {{
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.75rem 1.5rem;
                color: var(--text);
                text-decoration: none;
                transition: all 0.3s ease;
                position: relative;
                cursor: pointer;
            }}

            .sidebar-item:hover {{
                background: var(--hover-bg);
            }}

            .sidebar-item.active {{
                background: rgba(0, 229, 255, 0.1);
                color: var(--accent);
                font-weight: 500;
            }}

            .sidebar-item.active::before {{
                content: "";
                position: absolute;
                left: 0;
                top: 0;
                height: 100%;
                width: 3px;
                background: var(--accent);
            }}

            .sidebar-icon {{
                font-size: 1.1rem;
                width: 20px;
                text-align: center;
            }}

            .main-content {{
                flex: 1;
                min-width: 0;
                height: 100%;
                overflow-y: auto;
                padding: 1.5rem;
            }}

            .content-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }}

            .content-title {{
                font-size: 1.5rem;
                font-weight: 600;
            }}

            .content-actions {{
                display: flex;
                gap: 0.75rem;
            }}

            .btn {{
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.6rem 1.2rem;
                background: transparent;
                border: 1px solid var(--border);
                color: var(--text);
                border-radius: 6px;
                font-family: 'Outfit', sans-serif;
                font-size: 0.9rem;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}

            .btn:hover {{
                border-color: var(--accent);
                color: var(--accent);
            }}

            .btn-primary {{
                background: rgba(0, 229, 255, 0.1);
                border-color: var(--accent);
                color: var(--accent);
            }}

            .btn-primary:hover {{
                background: rgba(0, 229, 255, 0.2);
                box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
            }}

            .card {{
                background: var(--card-bg);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
            }}

            .card:hover {{
                border-color: rgba(0, 229, 255, 0.4);
                box-shadow: 0 0 15px rgba(0, 229, 255, 0.1);
            }}

            .card-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.25rem;
            }}

            .card-title {{
                font-size: 1.2rem;
                font-weight: 600;
            }}

            .card-description {{
                color: rgba(224, 247, 250, 0.8);
                margin-bottom: 1.5rem;
                line-height: 1.5;
            }}

            .form-group {{
                margin-bottom: 1.25rem;
            }}

            .form-label {{
                display: block;
                margin-bottom: 0.5rem;
                font-weight: 500;
            }}

            .form-control {{
                width: 100%;
                padding: 0.75rem 1rem;
                background: rgba(10, 14, 23, 0.7);
                border: 1px solid var(--border);
                border-radius: 6px;
                color: var(--text);
                font-family: 'Outfit', sans-serif;
                transition: all 0.3s ease;
            }}

            .form-control:focus {{
                outline: none;
                border-color: var(--accent);
                box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.2);
            }}

            .form-row {{
                display: flex;
                gap: 1rem;
            }}

            .form-row .form-group {{
                flex: 1;
            }}

            .result-box {{
                background: rgba(0, 229, 255, 0.1);
                border: 1px solid var(--accent);
                border-radius: 8px;
                padding: 1.25rem;
                margin-top: 1.5rem;
            }}

            .result-title {{
                color: var(--accent);
                font-weight: 600;
                margin-bottom: 0.75rem;
            }}

            .result-value {{
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--accent);
                margin: 0.5rem 0;
            }}

            .result-details {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 0.75rem;
                margin-top: 1rem;
            }}

            .result-detail {{
                display: flex;
                justify-content: space-between;
                padding: 0.5rem 0;
                border-bottom: 1px solid rgba(0, 229, 255, 0.2);
            }}

            .tabs {{
                display: flex;
                border-bottom: 1px solid var(--border);
                margin-bottom: 1.5rem;
            }}

            .tab {{
                padding: 0.75rem 1.5rem;
                background: transparent;
                border: none;
                color: var(--text);
                font-family: 'Outfit', sans-serif;
                font-size: 0.9rem;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
            }}

            .tab:hover {{ color: var(--accent); }}

            .tab.active {{
                color: var(--accent);
                font-weight: 500;
            }}

            .tab.active::after {{
                content: "";
                position: absolute;
                bottom: -1px;
                left: 0;
                width: 100%;
                height: 2px;
                background: var(--accent);
            }}

            .data-table-container {{
                position: relative;
                margin: 1.5rem 0;
                border: 1px solid var(--border);
                border-radius: 8px;
                overflow: hidden;
            }}

            .table-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1rem;
                background: rgba(10, 14, 23, 0.8);
                border-bottom: 1px solid var(--border);
            }}

            .table-title {{
                font-weight: 600;
                color: var(--accent);
            }}

            .table-download-btn {{
                background: transparent;
                border: 1px solid var(--border);
                color: var(--text);
                padding: 0.4rem 0.8rem;
                border-radius: 4px;
                font-size: 0.8rem;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 0.4rem;
            }}

            .table-download-btn:hover {{
                background: var(--hover-bg);
                border-color: var(--accent);
                color: var(--accent);
            }}

            .data-table {{
                width: 100%;
                border-collapse: collapse;
                background: rgba(10, 14, 23, 0.6);
            }}

            .data-table th {{
                background: rgba(26, 43, 71, 0.8);
                padding: 0.75rem 1rem;
                text-align: left;
                font-weight: 600;
                color: var(--accent);
                border-bottom: 1px solid var(--border);
            }}

            .data-table td {{
                padding: 0.75rem 1rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }}

            .data-table tr:last-child td {{
                border-bottom: none;
            }}

            .data-table tr:hover {{
                background: rgba(0, 229, 255, 0.05);
            }}

            .right-panel {{
                width: 320px;
                flex-shrink: 0;
                height: 100%;
                overflow-y: auto;
                padding: 1.5rem;
                border-left: 1px solid var(--border);
            }}

            .panel-card {{
                background: var(--card-bg);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                backdrop-filter: blur(10px);
            }}

            .panel-title {{
                font-size: 1.1rem;
                font-weight: 600;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}

            .activity-list {{
                list-style: none;
            }}

            .activity-item {{
                padding: 0.75rem 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                gap: 0.75rem;
            }}

            .activity-item:last-child {{
                border-bottom: none;
            }}

            .activity-icon {{
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: rgba(0, 229, 255, 0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                color: var(--accent);
            }}

            .activity-content {{
                flex: 1;
            }}

            .activity-title {{
                font-weight: 500;
                margin-bottom: 0.25rem;
            }}

            .activity-meta {{
                font-size: 0.8rem;
                opacity: 0.7;
            }}

            .tab-content {{
                display: none;
            }}

            .tab-content.active {{
                display: block;
                animation: fadeIn 0.3s ease-in;
            }}

            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            @media (max-width: 1024px) {{
                .dashboard-container {{ flex-direction: column; }}
                .sidebar, .right-panel {{ width: 100%; height: auto; }}
                .navbar-search {{ width: 200px; }}
            }}

            @media (max-width: 768px) {{
                .navbar {{ flex-wrap: wrap; gap: 1rem; }}
                .navbar-search {{ width: 100%; order: 3; }}
                .form-row {{ flex-direction: column; gap: 0; }}
                .data-table {{ display: block; overflow-x: auto; }}
            }}
        </style>
    </head>
    <body>
        <nav class="navbar">
            <div class="navbar-left">
                <div class="navbar-logo" onclick="navigateTo('orbital')">
                    <span style="font-size: 1.4rem;">◉</span>
                    AstroQuipu
                </div>
                <div class="navbar-search">
                    <input type="text" placeholder="Buscar análisis, cálculos...">
                </div>
            </div>
            <div class="navbar-right">
                <button class="navbar-button">+ Nuevo</button>
                <button class="navbar-button">↑ Importar</button>
                <div class="navbar-avatar">AQ</div>
            </div>
        </nav>

        <div class="dashboard-container">
            <aside class="sidebar">
                <div class="sidebar-header">
                    <div class="sidebar-title">Laboratorio Astronómico</div>
                    <div class="sidebar-subtitle">Herramientas de cálculo</div>
                </div>
                <div class="sidebar-menu">
                    <div class="sidebar-item active" onclick="switchTab('hubble')">
                        <span class="sidebar-icon">◉</span>
                        <span>Constante de Hubble</span>
                    </div>
                    <div class="sidebar-item" onclick="switchTab('redshift')">
                        <span class="sidebar-icon">↭</span>
                        <span>Redshift</span>
                    </div>
                    <div class="sidebar-item" onclick="switchTab('angular')">
                        <span class="sidebar-icon">⟳</span>
                        <span>Velocidad Angular</span>
                    </div>
                    <div class="sidebar-item" onclick="switchTab('orbits')">
                        <span class="sidebar-icon">⌾</span>
                        <span>Órbitas</span>
                    </div>
                    <div class="sidebar-item" onclick="switchTab('csv')">
                        <span class="sidebar-icon">▣</span>
                        <span>Análisis CSV</span>
                    </div>
                    <div class="sidebar-item">
                        <span class="sidebar-icon">📊</span>
                        <span>Mis Análisis</span>
                    </div>
                    <div class="sidebar-item">
                        <span class="sidebar-icon">⚙</span>
                        <span>Configuración</span>
                    </div>
                </div>
            </aside>

            <main class="main-content">
                <div class="content-header">
                    <h1 class="content-title" id="content-main-title">Cálculo de la Constante de Hubble</h1>
                    <div class="content-actions">
                        <button class="btn" onclick="downloadResults()">
                            <span>⤓</span> Descargar
                        </button>
                        <button class="btn btn-primary">
                            <span>+</span> Nuevo
                        </button>
                    </div>
                </div>

                <div class="tabs">
                    <button class="tab active" data-tab="hubble" onclick="switchTab('hubble')">Cálculo básico</button>
                    <button class="tab" data-tab="csv" onclick="switchTab('csv')">Análisis CSV</button>
                </div>

                <!-- PESTAÑA: Constante de Hubble -->
                <div class="tab-content active" id="hubble-tab">
                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Parámetros de entrada</h2>
                        </div>
                        <p class="card-description">
                            Introduce los valores de velocidad de recesión y distancia para calcular la constante de Hubble (H₀).
                        </p>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label" for="velocidad">Velocidad de recesión (km/s)</label>
                                <input type="number" id="velocidad" class="form-control" placeholder="1500" value="1500">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="distancia">Distancia (Mpc)</label>
                                <input type="number" id="distancia" class="form-control" placeholder="22.0" value="22.0">
                            </div>
                        </div>
                        
                        <button class="btn btn-primary" onclick="calculateHubble()" style="margin-top: 1rem;">
                            Calcular H₀
                        </button>
                        
                        <div class="result-box" id="hubble-result" style="display: none;">
                            <h3 class="result-title">Resultado del cálculo</h3>
                            <div class="result-value" id="hubble-value">H₀ = 68.18 km/s/Mpc</div>
                            <div class="result-details">
                                <div class="result-detail">
                                    <span>Velocidad:</span>
                                    <span id="result-velocidad">1,500 km/s</span>
                                </div>
                                <div class="result-detail">
                                    <span>Distancia:</span>
                                    <span id="result-distancia">22.0 Mpc</span>
                                </div>
                                <div class="result-detail">
                                    <span>Fecha:</span>
                                    <span id="calculation-date"></span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Información sobre la Constante de Hubble</h2>
                        </div>
                        <p class="card-description">
                            La constante de Hubble (H₀) es uno de los parámetros más importantes en cosmología. 
                            Representa la tasa de expansión del universo y se expresa en km/s por megaparsec (Mpc).
                        </p>
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">Valor aceptado actualmente</label>
                                <input type="text" class="form-control" value="67.4 ± 0.5 km/s/Mpc" readonly>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Método de medición</label>
                                <input type="text" class="form-control" value="Planck (CMB)" readonly>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- PESTAÑA: Redshift -->
                <div class="tab-content" id="redshift-tab">
                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Cálculo de Redshift</h2>
                        </div>
                        <p class="card-description">
                            El redshift (z) mide cuánto se ha desplazado la longitud de onda de la luz de una galaxia hacia el rojo debido a su alejamiento.
                        </p>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label" for="longitud_obs">Longitud de onda observada (nm)</label>
                                <input type="number" id="longitud_obs" class="form-control" placeholder="658.0" value="658.0" step="0.1">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="longitud_emit">Longitud de onda emitida (nm)</label>
                                <input type="number" id="longitud_emit" class="form-control" placeholder="656.3" value="656.3" step="0.1">
                            </div>
                        </div>
                        
                        <button class="btn btn-primary" onclick="calculateRedshift()" style="margin-top: 1rem;">
                            Calcular Redshift
                        </button>
                        
                        <div class="result-box" id="redshift-result" style="display: none;">
                            <h3 class="result-title">Resultado del cálculo</h3>
                            <div class="result-value" id="redshift-value">z = 0.002591</div>
                            <div class="result-details">
                                <div class="result-detail">
                                    <span>Longitud observada:</span>
                                    <span id="result-long-obs">658.0 nm</span>
                                </div>
                                <div class="result-detail">
                                    <span>Longitud emitida:</span>
                                    <span id="result-long-emit">656.3 nm</span>
                                </div>
                                <div class="result-detail">
                                    <span>Velocidad (v ≈ cz):</span>
                                    <span id="result-velocity-z">776.8 km/s</span>
                                </div>
                                <div class="result-detail">
                                    <span>Distancia (Ley Hubble):</span>
                                    <span id="result-distance-z">11.1 Mpc</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Información sobre Redshift</h2>
                        </div>
                        <p class="card-description">
                            La línea H-alpha del hidrógeno tiene una longitud de onda de 656.3 nm en el laboratorio. 
                            Esta línea es comúnmente usada para medir el redshift de galaxias.
                        </p>
                    </div>
                </div>

                <!-- PESTAÑA: Velocidad Angular -->
                <div class="tab-content" id="angular-tab">
                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Cálculo de Velocidad Angular</h2>
                        </div>
                        <p class="card-description">
                            Calcula la velocidad angular de un objeto en órbita a partir de su velocidad lineal y radio orbital.
                        </p>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label" for="vel_lineal">Velocidad lineal (km/s)</label>
                                <input type="number" id="vel_lineal" class="form-control" placeholder="220" value="220">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="radio_orbit">Radio de órbita (km)</label>
                                <input type="number" id="radio_orbit" class="form-control" placeholder="2.46e17" value="2.46e17" step="1e15">
                            </div>
                        </div>
                        
                        <button class="btn btn-primary" onclick="calculateAngular()" style="margin-top: 1rem;">
                            Calcular Velocidad Angular
                        </button>
                        
                        <div class="result-box" id="angular-result" style="display: none;">
                            <h3 class="result-title">Resultado del cálculo</h3>
                            <div class="result-value" id="angular-value">ω = 8.94 × 10⁻¹³ rad/s</div>
                            <div class="result-details">
                                <div class="result-detail">
                                    <span>Velocidad lineal:</span>
                                    <span id="result-vel-linear">220 km/s</span>
                                </div>
                                <div class="result-detail">
                                    <span>Radio:</span>
                                    <span id="result-radio">2.46 × 10¹⁷ km</span>
                                </div>
                                <div class="result-detail">
                                    <span>Período orbital:</span>
                                    <span id="result-period">222 millones de años</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Ejemplo: El Sol en la Vía Láctea</h2>
                        </div>
                        <p class="card-description">
                            El Sol orbita alrededor del centro galáctico a aproximadamente 220 km/s, 
                            a una distancia de unos 26,000 años luz (≈ 2.46 × 10¹⁷ km).
                        </p>
                    </div>
                </div>

                <!-- PESTAÑA: Órbitas -->
                <div class="tab-content" id="orbits-tab">
                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Cálculo de Parámetros Orbitales</h2>
                        </div>
                        <p class="card-description">
                            Calcula la velocidad orbital y período de un objeto en órbita circular alrededor de una masa central.
                        </p>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label" for="masa_central">Masa central (kg)</label>
                                <input type="number" id="masa_central" class="form-control" placeholder="5.972e24" value="5.972e24" step="1e23">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="radio_orbital">Radio de órbita (m)</label>
                                <input type="number" id="radio_orbital" class="form-control" placeholder="6771000" value="6771000">
                            </div>
                        </div>
                        
                        <button class="btn btn-primary" onclick="calculateOrbit()" style="margin-top: 1rem;">
                            Calcular Órbita
                        </button>
                        
                        <div class="result-box" id="orbit-result" style="display: none;">
                            <h3 class="result-title">Resultado del cálculo</h3>
                            <div class="result-value" id="orbit-velocity">v = 7.67 km/s</div>
                            <div class="result-details">
                                <div class="result-detail">
                                    <span>Velocidad orbital:</span>
                                    <span id="result-v-orbit">7.67 km/s</span>
                                </div>
                                <div class="result-detail">
                                    <span>Período orbital:</span>
                                    <span id="result-t-orbit">1.55 horas</span>
                                </div>
                                <div class="result-detail">
                                    <span>Altura sobre superficie:</span>
                                    <span id="result-altitude">400 km</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Ejemplo: Estación Espacial Internacional</h2>
                        </div>
                        <p class="card-description">
                            La ISS orbita a aproximadamente 400 km sobre la superficie terrestre, 
                            completando una órbita cada ~92 minutos a una velocidad de ~7.66 km/s.
                        </p>
                    </div>
                </div>

                <!-- PESTAÑA: Análisis CSV -->
                <div class="tab-content" id="csv-tab">
                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">Análisis de Datos de Galaxias</h2>
                        </div>
                        <p class="card-description">
                            Análisis completo de los datos de galaxias del archivo CSV. Se calcula automáticamente la constante de Hubble para cada galaxia.
                        </p>

                        <button class="btn btn-primary" onclick="loadCSVData()">
                            ▣ Analizar CSV
                        </button>

                        <div class="data-table-container" id="original-data-container" style="display: none;">
                            <div class="table-header">
                                <div class="table-title">Datos Originales</div>
                                <button class="table-download-btn" onclick="downloadOriginalData()">
                                    <span>⤓</span> CSV
                                </button>
                            </div>
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Galaxia</th>
                                        <th>Velocidad (km/s)</th>
                                        <th>Distancia (Mpc)</th>
                                        <th>Long. Obs (nm)</th>
                                        <th>Long. Emit (nm)</th>
                                    </tr>
                                </thead>
                                <tbody id="original-data-body"></tbody>
                            </table>
                        </div>

                        <div class="data-table-container" id="analysis-results-container" style="display: none;">
                            <div class="table-header">
                                <div class="table-title">Resultados del Análisis</div>
                                <button class="table-download-btn" onclick="downloadAnalysisResults()">
                                    <span>⤓</span> CSV
                                </button>
                            </div>
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Galaxia</th>
                                        <th>Velocidad</th>
                                        <th>Distancia</th>
                                        <th>H₀ (km/s/Mpc)</th>
                                        <th>Redshift (z)</th>
                                        <th>Dist. via z (Mpc)</th>
                                    </tr>
                                </thead>
                                <tbody id="analysis-results-body"></tbody>
                            </table>
                        </div>

                        <div class="result-box" id="csv-statistics" style="display: none;">
                            <h3 class="result-title">Estadísticas del Análisis</h3>
                            <div class="result-details">
                                <div class="result-detail">
                                    <span>Total galaxias:</span>
                                    <span id="total-galaxies">0</span>
                                </div>
                                <div class="result-detail">
                                    <span>H₀ promedio:</span>
                                    <span id="average-hubble">0.00 km/s/Mpc</span>
                                </div>
                                <div class="result-detail">
                                    <span>Desviación:</span>
                                    <span id="std-deviation">±0.00 km/s/Mpc</span>
                                </div>
                                <div class="result-detail">
                                    <span>Máximo:</span>
                                    <span id="max-hubble">0.00 km/s/Mpc</span>
                                </div>
                                <div class="result-detail">
                                    <span>Mínimo:</span>
                                    <span id="min-hubble">0.00 km/s/Mpc</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            <aside class="right-panel">
                <div class="panel-card">
                    <h3 class="panel-title">
                        <span>◍</span> Actividad Reciente
                    </h3>
                    <ul class="activity-list">
                        <li class="activity-item">
                            <div class="activity-icon">◉</div>
                            <div class="activity-content">
                                <div class="activity-title">Cálculo de H₀</div>
                                <div class="activity-meta">Hace 2 horas</div>
                            </div>
                        </li>
                        <li class="activity-item">
                            <div class="activity-icon">↭</div>
                            <div class="activity-content">
                                <div class="activity-title">Análisis redshift</div>
                                <div class="activity-meta">Hace 1 día</div>
                            </div>
                        </li>
                        <li class="activity-item">
                            <div class="activity-icon">▣</div>
                            <div class="activity-content">
                                <div class="activity-title">Datos importados</div>
                                <div class="activity-meta">Hace 2 días</div>
                            </div>
                        </li>
                    </ul>
                </div>

                <div class="panel-card">
                    <h3 class="panel-title">
                        <span>◇</span> Novedades
                    </h3>
                    <ul class="activity-list">
                        <li class="activity-item">
                            <div class="activity-icon">+</div>
                            <div class="activity-content">
                                <div class="activity-title">Exportación PDF</div>
                                <div class="activity-meta">Disponible</div>
                            </div>
                        </li>
                        <li class="activity-item">
                            <div class="activity-icon">⚙</div>
                            <div class="activity-content">
                                <div class="activity-title">Mantenimiento</div>
                                <div class="activity-meta">20 Nov 02:00</div>
                            </div>
                        </li>
                    </ul>
                </div>
            </aside>
        </div>

        <script>
            // Constantes físicas (coinciden con calculos.py)
            const C_LIGHT = 299792.458;  // km/s
            const H0_DEFAULT = 70;  // km/s/Mpc
            const G_CONSTANT = 6.674e-11;  // m^3 kg^-1 s^-2

            // Datos cargados desde Python
            let galaxyData = {csv_data_json};
            let analysisResults = {analysis_results_json};
            let csvDataLoaded = false;  // Control para evitar carga automática

            console.log('🚀 Dashboard cargado');
            console.log('📊 Datos disponibles:', galaxyData ? galaxyData.length : 0, 'galaxias');

            // Función para cambiar entre pestañas
            function switchTab(tabName) {{
                console.log('🔄 Cambiando a pestaña:', tabName);
                
                // Ocultar todos los contenidos
                document.querySelectorAll('.tab-content').forEach(content => {{
                    content.classList.remove('active');
                }});
                
                // Actualizar tabs
                document.querySelectorAll('.tab').forEach(tab => {{
                    tab.classList.remove('active');
                }});
                
                // Actualizar sidebar
                document.querySelectorAll('.sidebar-item').forEach(item => {{
                    item.classList.remove('active');
                }});
                
                // Mostrar contenido seleccionado
                const targetTab = document.getElementById(tabName + '-tab');
                if (targetTab) {{
                    targetTab.classList.add('active');
                }}
                
                // Activar tab correspondiente
                const activeTab = document.querySelector('[data-tab="' + tabName + '"]');
                if (activeTab) {{
                    activeTab.classList.add('active');
                }}
                
                // Activar sidebar item
                const sidebarItems = document.querySelectorAll('.sidebar-item');
                sidebarItems.forEach(item => {{
                    const text = item.textContent.toLowerCase().trim();
                    if (
                        (tabName === 'hubble' && text.includes('hubble')) ||
                        (tabName === 'redshift' && text.includes('redshift')) ||
                        (tabName === 'angular' && text.includes('angular')) ||
                        (tabName === 'orbits' && text.includes('órbitas')) ||
                        (tabName === 'csv' && text.includes('csv'))
                    ) {{
                        item.classList.add('active');
                    }}
                }});
                
                // Actualizar título
                const titleMap = {{
                    'hubble': 'Cálculo de la Constante de Hubble',
                    'csv': 'Análisis de Datos CSV',
                    'redshift': 'Cálculo de Redshift',
                    'angular': 'Velocidad Angular',
                    'orbits': 'Parámetros Orbitales'
                }};
                
                const titleElement = document.getElementById('content-main-title');
                if (titleElement && titleMap[tabName]) {{
                    titleElement.textContent = titleMap[tabName];
                }}
            }}

            // === CÁLCULO DE HUBBLE ===
            function calculateHubble() {{
                const velocidad = parseFloat(document.getElementById('velocidad').value) || 0;
                const distancia = parseFloat(document.getElementById('distancia').value) || 1;
                
                if (distancia === 0) {{
                    alert('⚠️ La distancia no puede ser cero');
                    return;
                }}
                
                const H0 = velocidad / distancia;
                
                document.getElementById('hubble-value').textContent = `H₀ = ${{H0.toFixed(2)}} km/s/Mpc`;
                document.getElementById('result-velocidad').textContent = `${{velocidad.toLocaleString()}} km/s`;
                document.getElementById('result-distancia').textContent = `${{distancia}} Mpc`;
                document.getElementById('calculation-date').textContent = new Date().toLocaleDateString('es-ES');
                
                document.getElementById('hubble-result').style.display = 'block';
                console.log('✅ Hubble calculado:', H0);
            }}

            // === CÁLCULO DE REDSHIFT ===
            function calculateRedshift() {{
                const longObs = parseFloat(document.getElementById('longitud_obs').value) || 0;
                const longEmit = parseFloat(document.getElementById('longitud_emit').value) || 1;
                
                if (longEmit === 0) {{
                    alert('⚠️ La longitud emitida no puede ser cero');
                    return;
                }}
                
                const z = (longObs - longEmit) / longEmit;
                const velocidad = C_LIGHT * z;
                const distancia = velocidad / H0_DEFAULT;
                
                document.getElementById('redshift-value').textContent = `z = ${{z.toFixed(6)}}`;
                document.getElementById('result-long-obs').textContent = `${{longObs}} nm`;
                document.getElementById('result-long-emit').textContent = `${{longEmit}} nm`;
                document.getElementById('result-velocity-z').textContent = `${{velocidad.toFixed(2)}} km/s`;
                document.getElementById('result-distance-z').textContent = `${{distancia.toFixed(2)}} Mpc`;
                
                document.getElementById('redshift-result').style.display = 'block';
                console.log('✅ Redshift calculado:', z);
            }}

            // === CÁLCULO DE VELOCIDAD ANGULAR ===
            function calculateAngular() {{
                const velLineal = parseFloat(document.getElementById('vel_lineal').value) || 0;
                const radio = parseFloat(document.getElementById('radio_orbit').value) || 1;
                
                if (radio === 0) {{
                    alert('⚠️ El radio no puede ser cero');
                    return;
                }}
                
                const omega = (velLineal * 1000) / (radio * 1000);  // rad/s
                const periodo = (2 * Math.PI) / omega;  // segundos
                const periodoAnios = periodo / (365.25 * 24 * 3600);  // años
                
                document.getElementById('angular-value').textContent = `ω = ${{omega.toExponential(2)}} rad/s`;
                document.getElementById('result-vel-linear').textContent = `${{velLineal}} km/s`;
                document.getElementById('result-radio').textContent = `${{radio.toExponential(2)}} km`;
                document.getElementById('result-period').textContent = `${{(periodoAnios / 1e6).toFixed(0)}} millones de años`;
                
                document.getElementById('angular-result').style.display = 'block';
                console.log('✅ Velocidad angular calculada:', omega);
            }}

            // === CÁLCULO DE ÓRBITA ===
            function calculateOrbit() {{
                const masaCentral = parseFloat(document.getElementById('masa_central').value) || 0;
                const radioOrbital = parseFloat(document.getElementById('radio_orbital').value) || 1;
                
                if (radioOrbital <= 0 || masaCentral <= 0) {{
                    alert('⚠️ La masa y el radio deben ser positivos');
                    return;
                }}
                
                // v = sqrt(GM/r)
                const vOrbital = Math.sqrt(G_CONSTANT * masaCentral / radioOrbital);  // m/s
                const periodo = (2 * Math.PI * radioOrbital) / vOrbital;  // segundos
                
                const vOrbitalKms = vOrbital / 1000;  // km/s
                const periodoHoras = periodo / 3600;  // horas
                const altura = (radioOrbital - 6.371e6) / 1000;  // km
                
                document.getElementById('orbit-velocity').textContent = `v = ${{vOrbitalKms.toFixed(2)}} km/s`;
                document.getElementById('result-v-orbit').textContent = `${{vOrbitalKms.toFixed(2)}} km/s`;
                document.getElementById('result-t-orbit').textContent = `${{periodoHoras.toFixed(2)}} horas`;
                document.getElementById('result-altitude').textContent = `${{altura.toFixed(0)}} km`;
                
                document.getElementById('orbit-result').style.display = 'block';
                console.log('✅ Órbita calculada - Velocidad:', vOrbitalKms, 'km/s, Período:', periodoHoras, 'horas');
            }}

            // === CARGAR DATOS CSV ===
            function loadCSVData() {{
                console.log('📊 Botón Analizar CSV presionado');
                
                if (!galaxyData || galaxyData.length === 0) {{
                    alert('⚠️ No hay datos disponibles');
                    return;
                }}
                
                csvDataLoaded = true;
                
                // Mostrar contenedores
                document.getElementById('original-data-container').style.display = 'block';
                document.getElementById('analysis-results-container').style.display = 'block';
                document.getElementById('csv-statistics').style.display = 'block';
                
                // Llenar tabla de datos originales
                const originalBody = document.getElementById('original-data-body');
                originalBody.innerHTML = '';
                
                galaxyData.forEach(galaxia => {{
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${{galaxia.galaxia}}</td>
                        <td>${{galaxia.velocidad}}</td>
                        <td>${{galaxia.distancia}}</td>
                        <td>${{galaxia.longitud_obs || 'N/A'}}</td>
                        <td>${{galaxia.longitud_emit || 'N/A'}}</td>
                    `;
                    originalBody.appendChild(row);
                }});
                
                // Mostrar resultados del análisis
                if (analysisResults && analysisResults.length > 0) {{
                    displayAnalysisResults();
                }} else {{
                    console.log('⚠️ No hay resultados de análisis precalculados');
                }}
                
                console.log('✅ Datos CSV cargados correctamente');
            }}

            // === MOSTRAR RESULTADOS DEL ANÁLISIS ===
            function displayAnalysisResults() {{
                const resultsBody = document.getElementById('analysis-results-body');
                resultsBody.innerHTML = '';
                
                let H0Sum = 0;
                let H0Values = [];
                
                analysisResults.forEach(resultado => {{
                    const row = document.createElement('tr');
                    const H0 = resultado.H0_calculado || 0;
                    
                    row.innerHTML = `
                        <td>${{resultado.galaxia}}</td>
                        <td>${{resultado.velocidad_km_s || resultado.velocidad}}</td>
                        <td>${{resultado.distancia_Mpc || resultado.distancia}}</td>
                        <td>${{H0.toFixed(2)}}</td>
                        <td>${{resultado.redshift ? resultado.redshift.toFixed(6) : 'N/A'}}</td>
                        <td>${{resultado.distancia_via_redshift ? resultado.distancia_via_redshift.toFixed(2) : 'N/A'}}</td>
                    `;
                    resultsBody.appendChild(row);
                    
                    H0Sum += H0;
                    H0Values.push(H0);
                }});
                
                // Calcular estadísticas
                if (H0Values.length > 0) {{
                    const promedio = H0Sum / H0Values.length;
                    const max = Math.max(...H0Values);
                    const min = Math.min(...H0Values);
                    
                    const squaredDiffs = H0Values.map(value => Math.pow(value - promedio, 2));
                    const avgSquaredDiff = squaredDiffs.reduce((sum, value) => sum + value, 0) / H0Values.length;
                    const stdDev = Math.sqrt(avgSquaredDiff);
                    
                    document.getElementById('total-galaxies').textContent = analysisResults.length;
                    document.getElementById('average-hubble').textContent = `${{promedio.toFixed(2)}} km/s/Mpc`;
                    document.getElementById('std-deviation').textContent = `±${{stdDev.toFixed(2)}} km/s/Mpc`;
                    document.getElementById('max-hubble').textContent = `${{max.toFixed(2)}} km/s/Mpc`;
                    document.getElementById('min-hubble').textContent = `${{min.toFixed(2)}} km/s/Mpc`;
                }}
            }}

            // === FUNCIONES DE DESCARGA ===
            function downloadOriginalData() {{
                if (!galaxyData || galaxyData.length === 0) {{
                    alert('⚠️ No hay datos para descargar');
                    return;
                }}
                const csv = convertToCSV(galaxyData, ['galaxia', 'velocidad', 'distancia', 'longitud_obs', 'longitud_emit']);
                downloadCSV(csv, 'datos_galaxias_original.csv');
            }}

            function downloadAnalysisResults() {{
                if (!analysisResults || analysisResults.length === 0) {{
                    alert('⚠️ No hay resultados para descargar');
                    return;
                }}
                const csv = convertToCSV(analysisResults, 
                    ['galaxia', 'velocidad_km_s', 'distancia_Mpc', 'H0_calculado', 'redshift', 'distancia_via_redshift']);
                downloadCSV(csv, 'resultados_analisis.csv');
            }}

            function downloadResults() {{
                const activeTab = document.querySelector('.tab.active');
                if (activeTab && activeTab.getAttribute('data-tab') === 'csv') {{
                    downloadAnalysisResults();
                }} else {{
                    alert('ℹ️ Cambia a la pestaña de Análisis CSV para descargar resultados');
                }}
            }}

            function convertToCSV(data, headers) {{
                if (!data || data.length === 0) return '';
                const headerRow = headers.join(',');
                const dataRows = data.map(row => 
                    headers.map(header => row[header] !== undefined ? row[header] : '').join(',')
                );
                return [headerRow, ...dataRows].join('\\n');
            }}

            function downloadCSV(csvContent, filename) {{
                const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                console.log('✅ Descargado:', filename);
            }}

            // === NAVEGACIÓN ===
            function navigateTo(page) {{
                console.log('🔄 Navegando a:', page);
                window.parent.postMessage({{ action: 'navigate', page: page }}, '*');
            }}

            // === INICIALIZACIÓN ===
            document.addEventListener('DOMContentLoaded', function() {{
                console.log('✅ Dashboard inicializado correctamente');
                console.log('📌 NO se cargan datos CSV automáticamente - esperando clic del usuario');
            }});

            console.log('🎯 Script cargado - Todas las funciones disponibles');
        </script>
    </body>
    </html>
    """
    
    return html_content

# ============================================
# ROUTER DE PÁGINAS
# ============================================

if st.session_state.current_page == 'orbital':
    # PÁGINA PRINCIPAL - MENÚ ORBITAL
    components.html(load_orbital_interface(), height=1080, scrolling=False)

elif st.session_state.current_page == 'analisis':
    # PÁGINA DE ANÁLISIS/DASHBOARD
    dashboard_html = load_dashboard_html()
    components.html(dashboard_html, height=1080, scrolling=False)

# Otras páginas (placeholder)
elif st.session_state.current_page == 'mis_analisis':
    st.markdown('<div style="color: white; padding: 2rem;"><h1>📁 Mis Análisis</h1></div>', unsafe_allow_html=True)
    if st.button("← Volver"):
        st.session_state.current_page = 'orbital'
        st.rerun()

elif st.session_state.current_page == 'aprende':
    st.markdown('<div style="color: white; padding: 2rem;"><h1>🎓 Aprende del Universo</h1></div>', unsafe_allow_html=True)
    if st.button("← Volver"):
        st.session_state.current_page = 'orbital'
        st.rerun()

elif st.session_state.current_page == 'simula':
    st.markdown('<div style="color: white; padding: 2rem;"><h1>🌠 Simula el Universo</h1></div>', unsafe_allow_html=True)
    if st.button("← Volver"):
        st.session_state.current_page = 'orbital'
        st.rerun()

elif st.session_state.current_page == 'perfil':
    st.markdown('<div style="color: white; padding: 2rem;"><h1>👤 Mi Perfil</h1></div>', unsafe_allow_html=True)
    if st.button("← Volver"):
        st.session_state.current_page = 'orbital'
        st.rerun()

elif st.session_state.current_page == 'descripcion':
    st.markdown('<div style="color: white; padding: 2rem;"><h1>📖 Descripción</h1></div>', unsafe_allow_html=True)
    if st.button("← Volver"):
        st.session_state.current_page = 'orbital'
        st.rerun()

elif st.session_state.current_page == 'funciones':
    st.markdown('<div style="color: white; padding: 2rem;"><h1>⚙️ Funciones</h1></div>', unsafe_allow_html=True)
    if st.button("← Volver"):
        st.session_state.current_page = 'orbital'
        st.rerun()
