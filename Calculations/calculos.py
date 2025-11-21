
import pandas as pd
import numpy as np
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

class Calculos:
    """Clase para realizar cálculos astronómicos."""
    
    # Constantes físicas
    C = 299792.458      # Velocidad luz km/s
    H0 = 70             # Hubble km/s/Mpc
    G = 6.67430e-11     # Constante gravitacional m^3 kg^-1 s^-2
    AU = 1.496e11       # Metros
    MASA_SOL = 1.989e30 # Kg

    # ... [MANTENEMOS TODO EL CÓDIGO ANTERIOR DE VISUALIZACIÓN Y SIMULACIÓN INTACTO] ...
    
    def generar_coordenadas_cartesianas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convierte RA, DEC y Redshift (z) a coordenadas cartesianas."""
        df_map = df.copy()
        if not {'ra', 'dec', 'z'}.issubset(df_map.columns) and not {'RA', 'DEC', 'Z'}.issubset(df_map.columns):
            return None
        if 'RA' in df_map.columns: df_map.rename(columns={'RA': 'ra', 'DEC': 'dec', 'Z': 'z'}, inplace=True)
        df_map['distancia_estimada_Mpc'] = (self.C * df_map['z']) / self.H0
        ra_rad = np.deg2rad(df_map['ra'])
        dec_rad = np.deg2rad(df_map['dec'])
        dist = df_map['distancia_estimada_Mpc']
        df_map['x_coord'] = dist * np.cos(dec_rad) * np.cos(ra_rad)
        df_map['y_coord'] = dist * np.cos(dec_rad) * np.sin(ra_rad)
        df_map['z_coord'] = dist * np.sin(dec_rad)
        return df_map

    def simular_orbita_futura(self, df: pd.DataFrame, dias: int = 365) -> Dict:
        """Simula la posición de un objeto NEO resolviendo la Ecuación de Kepler."""
        if df.empty: return None
        row = df.iloc[0]
        req_cols = ['a', 'e', 'incl', 'Omega', 'w', 'M']
        if not all(c in row for c in req_cols): return {"error": "Faltan columnas orbitales"}
        
        a = float(row['a'])
        e = float(row['e'])
        i = np.deg2rad(float(row['incl']))
        Om = np.deg2rad(float(row['Omega']))
        w = np.deg2rad(float(row['w']))
        M0 = np.deg2rad(float(row['M']))
        mu_au_d = 0.0002959122082855911
        n = np.deg2rad(float(row['n'])) if 'n' in row else np.sqrt(mu_au_d / a**3)

        E_orbit = np.linspace(0, 2*np.pi, 100)
        x_orb_plane = a * (np.cos(E_orbit) - e)
        y_orb_plane = a * np.sqrt(1 - e**2) * np.sin(E_orbit)
        
        def rotar_orbita(x, y, Om, w, i):
            X = x * (np.cos(w)*np.cos(Om) - np.sin(w)*np.sin(Om)*np.cos(i)) - \
                y * (np.sin(w)*np.cos(Om) + np.cos(w)*np.sin(Om)*np.cos(i))
            Y = x * (np.cos(w)*np.sin(Om) + np.sin(w)*np.cos(Om)*np.cos(i)) - \
                y * (np.sin(w)*np.sin(Om) - np.cos(w)*np.cos(Om)*np.cos(i))
            Z = x * (np.sin(w)*np.sin(i)) + y * (np.cos(w)*np.sin(i))
            return X, Y, Z

        X_traj, Y_traj, Z_traj = rotar_orbita(x_orb_plane, y_orb_plane, Om, w, i)
        M_futuro = M0 + n * dias
        E_futuro = M_futuro
        for _ in range(10):
            E_futuro = E_futuro - (E_futuro - e*np.sin(E_futuro) - M_futuro) / (1 - e*np.cos(E_futuro))
        x_fut = a * (np.cos(E_futuro) - e)
        y_fut = a * np.sqrt(1 - e**2) * np.sin(E_futuro)
        X_fut, Y_fut, Z_fut = rotar_orbita(x_fut, y_fut, Om, w, i)

        return {
            "trayectoria_x": X_traj, "trayectoria_y": Y_traj, "trayectoria_z": Z_traj,
            "futuro_x": X_fut, "futuro_y": Y_fut, "futuro_z": Z_fut,
            "dias_simulados": dias, "objeto": row.get('targetname', 'Objeto Desconocido')
        }

    # ... [MANTENEMOS EL RESTO DE MÉTODOS DE LA CLASE: __init__, aplicar_cosmologia, aplicar_orbitales, etc.] ...
    
    def __init__(self, data_path: str = "routines/data"):
        self.data_path = Path(data_path)
        self.datasets = {}
        self.ultimo_analisis = None
        self._escanear_datasets()
    
    def _escanear_datasets(self):
        if not self.data_path.exists():
            self.data_path.mkdir(parents=True, exist_ok=True)
            return
        csv_files = list(self.data_path.glob("*.csv"))
        for file in csv_files:
            self.datasets[file.stem] = file

    def aplicar_cosmologia(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
        df_res = df.copy()
        reporte = []
        if 'z' in df_res.columns:
            df_res['Velocidad_Recesion_km_s'] = df_res['z'] * self.C
            df_res['Distancia_Hubble_Mpc'] = df_res['Velocidad_Recesion_km_s'] / self.H0
            z_mean = df_res['z'].mean()
            d_mean = df_res['Distancia_Hubble_Mpc'].mean()
            reporte.append("📊 REPORTE COSMOLÓGICO (SDSS/DESI)")
            reporte.append(f"Z medio: {z_mean:.4f}")
            reporte.append(f"Distancia media: {d_mean:.2f} Mpc")
            return df_res, "\n".join(reporte)
        return df, "❌ Error: No se encontró columna 'z'."

    def aplicar_orbitales(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
        df_res = df.copy()
        reporte = []
        if 'a' in df_res.columns:
            df_res['Periodo_Anios'] = np.power(df_res['a'], 1.5)
            df_res['Velocidad_Media_km_s'] = 29.78 / np.sqrt(df_res['a'])
            reporte.append("🛸 REPORTE ORBITAL (NEO)")
            reporte.append(f"Velocidad media: {df_res['Velocidad_Media_km_s'].mean():.2f} km/s")
            return df_res, "\n".join(reporte)
        elif 'pl_orbper' in df_res.columns:
            reporte.append("🪐 REPORTE EXOPLANETAS")
            return df_res, "\n".join(reporte)
        return df, "⚠️ Sin columnas orbitales."

    def aplicar_exoplanetas(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
        df_exo = df.copy()
        reporte = []
        if 'pl_orbsmax' not in df_exo.columns and 'pl_orbper' in df_exo.columns:
            periodo_anios = df_exo['pl_orbper'] / 365.25
            df_exo['distancia_estimada_AU'] = np.power(periodo_anios, 2/3)
        elif 'pl_orbsmax' in df_exo.columns:
            df_exo['distancia_estimada_AU'] = df_exo['pl_orbsmax']
        else:
            df_exo['distancia_estimada_AU'] = np.nan

        def clasificar_planeta(row):
            r = row.get('pl_rade')
            if pd.isna(r): return "Desconocido"
            if r < 1.25: return "Tipo Tierra (Rocoso)"
            elif r < 2.0: return "Super-Tierra"
            elif r < 6.0: return "Mini-Neptuno"
            elif r < 15.0: return "Gigante Gaseoso (Júpiter)"
            else: return "Enana Marrón / Otro"

        if 'pl_rade' in df_exo.columns:
            df_exo['Clase_Planeta'] = df_exo.apply(clasificar_planeta, axis=1)

        if 'distancia_estimada_AU' in df_exo.columns and 'st_teff' in df_exo.columns:
            factor_t = (df_exo['st_teff'] / 5778.0) ** 2
            limite_interno = 0.95 * factor_t
            limite_externo = 1.4 * factor_t
            conditions = [
                (df_exo['distancia_estimada_AU'] < limite_interno),
                (df_exo['distancia_estimada_AU'] >= limite_interno) & (df_exo['distancia_estimada_AU'] <= limite_externo),
                (df_exo['distancia_estimada_AU'] > limite_externo)
            ]
            choices = ['Zona Caliente', 'Zona Habitable (Ricitos de Oro)', 'Zona Fría']
            df_exo['Zona_Termica'] = np.select(conditions, choices, default='Desconocido')

        n_rocosos = len(df_exo[df_exo['Clase_Planeta'] == 'Tipo Tierra (Rocoso)']) if 'Clase_Planeta' in df_exo.columns else 0
        n_habitables = len(df_exo[df_exo['Zona_Termica'] == 'Zona Habitable (Ricitos de Oro)']) if 'Zona_Termica' in df_exo.columns else 0
        reporte.append("🪐 ANÁLISIS DE EXOPLANETAS")
        reporte.append(f"Tipo Tierra detectados: {n_rocosos}")
        reporte.append(f"Candidatos en Zona Habitable: {n_habitables}")
        return df_exo, "\n".join(reporte)

    def aplicar_fotometria_desi(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
        df_desi = df.copy()
        reporte = []
        def flux_to_mag(flux_col):
            return np.where(flux_col > 0, 22.5 - 2.5 * np.log10(flux_col), np.nan)
        cols_flux = ['flux_g', 'flux_r', 'flux_z', 'flux_w1']
        cols_mag = ['mag_g', 'mag_r', 'mag_z', 'mag_w1']
        calculado = False
        for f_col, m_col in zip(cols_flux, cols_mag):
            if f_col in df_desi.columns:
                df_desi[m_col] = flux_to_mag(df_desi[f_col])
                calculado = True
        if not calculado: return df, "❌ Error: Sin columnas de flujo."
        if 'mag_g' in df_desi.columns and 'mag_r' in df_desi.columns:
            df_desi['color_g_r'] = df_desi['mag_g'] - df_desi['mag_r']
        if 'mag_r' in df_desi.columns and 'mag_z' in df_desi.columns:
            df_desi['color_r_z'] = df_desi['mag_r'] - df_desi['mag_z']
        if 'mag_z' in df_desi.columns and 'mag_w1' in df_desi.columns:
            df_desi['color_z_w1'] = df_desi['mag_z'] - df_desi['mag_w1']
        df_clean = df_desi.dropna(subset=['color_g_r', 'color_r_z'])
        reporte.append("🔭 ANÁLISIS FOTOMÉTRICO DESI")
        reporte.append(f"Objetos procesados: {len(df_desi)}")
        return df_desi, "\n".join(reporte)

    # =========================================================================
    # 🆕 NUEVOS MÉTODOS PARA CALCULADORAS BÁSICAS (Escalares)
    # =========================================================================

    def calc_basic_hubble(self, v_recesion: float, distancia: float) -> float:
        """Calcula H0 dados v (km/s) y d (Mpc). H0 = v/d"""
        return v_recesion / distancia if distancia != 0 else 0

    def calc_basic_redshift(self, lambda_obs: float, lambda_emit: float) -> float:
        """Calcula z dada la longitud de onda observada y emitida."""
        if lambda_emit == 0: return 0
        return (lambda_obs - lambda_emit) / lambda_emit

    def calc_basic_angular_vel(self, v_lineal: float, radio: float) -> float:
        """Calcula velocidad angular (rad/s). v en km/s, r en km."""
        if radio == 0: return 0
        return v_lineal / radio

    def calc_basic_orbital(self, masa_central: float, radio_orbita: float) -> float:
        """Calcula velocidad orbital v = sqrt(GM/r). Masa en kg, Radio en m."""
        if radio_orbita == 0: return 0
        return np.sqrt((self.G * masa_central) / radio_orbita)

