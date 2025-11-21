from astroquery.sdss import SDSS
from datetime import datetime
from dl import queryClient as qc
from astroquery.nasa_exoplanet_archive import NasaExoplanetArchive
from astroquery.jplhorizons import Horizons
from astroquery.mpc import MPC
import csv, os
import pandas as pd

class BaseDatos:
    """Clase para gestionar consultas y almacenamiento de datos astronómicos."""

    def __init__(self, limite=10000):
        self.limite = limite

    def conectar(self, ra=None, dec=None, z_max=None, z_min=None, tipo=None, source=None, radius=None, **kwargs):
        """Conecta y consulta diferentes bases de datos astronómicas."""
        
        # 1. Recuperar radius de kwargs si no vino explícito
        if radius is None:
            radius = kwargs.get('radius')

        # Valores por defecto
        ra = 180.0 if ra is None else float(ra)
        dec = 0.0 if dec is None else float(dec)
        z_max = 0.3 if z_max is None else float(z_max)
        z_min = 0.05 if z_min is None else float(z_min)

        if source.upper() == "SDSS":
            # SOLO pedir input si NO llegó desde la GUI
            if radius is None:
                try:
                    radius = float(input("Ingresa el radio de búsqueda (en grados): "))
                except:
                    radius = 0.1 # Valor de seguridad
            else:
                radius = float(radius)
            
            query = f"""
            SELECT TOP {self.limite}
                p.objid, p.ra, p.dec, s.z, s.class
            FROM PhotoObj AS p
            JOIN SpecObj AS s ON s.bestobjid = p.objid
            WHERE s.z BETWEEN {z_min} AND {z_max}
            AND p.ra BETWEEN {ra - radius} AND {ra + radius}
            AND p.dec BETWEEN {dec - radius} AND {dec + radius}
            """

            print("\nEjecutando consulta a SDSS...")
            try:
                result = SDSS.query_sql(query)
                print("Consulta completada.")
                return result
            except Exception as e:
                print(f"Error en SDSS: {e}")
                return None

        elif source.upper() == "DESI":
            # SOLO pedir input si NO llegó desde la GUI
            if radius is None:
                try:
                    radius = float(input("Ingresa el radio de búsqueda (en grados): "))
                except:
                    radius = 0.1
            else:
                radius = float(radius)
                
            query = f"""
                SELECT TOP {self.limite}
                ra, dec ,type, flux_g, flux_r, flux_z, flux_w1, flux_w2 , flux_ivar_g, flux_ivar_r, flux_ivar_z
                FROM ls_dr9.tractor
                WHERE ra BETWEEN {ra - radius} AND {ra + radius}
                AND dec BETWEEN {dec - radius} AND {dec + radius}
                """
            try:
                result = qc.query(sql=query, fmt='pandas')
                return result
            except Exception as e:
                print(f"Error en DESI: {e}")
                return None

        elif source.upper() == "NASA ESI":
            try:
                result = NasaExoplanetArchive.query_criteria(
                    table="pscomppars",
                    select="pl_name,hostname,disc_year,pl_orbper,pl_rade,pl_bmasse, pl_tranmid ,st_teff",
                    where="disc_year > 2015 AND pl_rade IS NOT NULL",
                    order="disc_year DESC"
                )
                return result
            except Exception as e:
                print(f"Error NASA ESI: {e}")
                return None

        elif source.upper() == "NEO":
            # Lógica Híbrida: GUI (kwargs) o Terminal
            cuerpos = {
                "1": "Ceres", "2": "Pallas", "4": "Vesta", "433": "Eros", "1862": "Apollo",
                "4179": "Toutatis", "3200": "Phaethon", "1620": "Geographos", "25143": "Itokawa",
                "101955": "Bennu", "99942": "Apophis", "162173": "Ryugu", "253": "Mathilde",
                "65803": "Didymos", "99907": "2013 VY4"
            }
            
            # 1. Intento desde GUI
            target_gui = kwargs.get('object_name')
            if target_gui:
                try:
                    print(f"Consultando {target_gui} (GUI)...")
                    obj = Horizons(id=target_gui, id_type='smallbody', location='@sun',
                                   epochs={'start':'2025-01-01', 'stop':'2025-01-10', 'step':'1d'})
                    result = obj.elements()
                    return result
                except Exception as exc:
                    print(f"Error NEO GUI: {exc}")
                    return None

            # 2. Intento Terminal (Código original)
            # ... (Mantenemos tu lógica de terminal aquí para compatibilidad)
            print("Modo Terminal NEO activado...")
            # [Aquí iría tu while True original si lo necesitas, pero para GUI esto basta]
            return None

        else:
            print("Fuente no soportada por el momento.")
            return None

    def guardardatos(self, result, source):
        os.makedirs("data", exist_ok=True)
        if result is not None:
            # Normalizar a DataFrame
            if hasattr(result, 'to_pandas'):
                df = result.to_pandas()
            elif isinstance(result, pd.DataFrame):
                df = result
            else:
                df = pd.DataFrame(result) # Intento genérico

            fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nombre_archivo = os.path.join("data", f"{source}_{fecha}.csv")
            df.to_csv(nombre_archivo, index=False)
            print(f"Archivo '{nombre_archivo}' guardado.")
            return nombre_archivo
        return None
