import numpy as np
import pandas as pd
from typing import Tuple

class Calculos:
    """
    Clase para realizar cálculos astronómicos relacionados con
    la constante de Hubble, redshift, velocidades angulares y órbitas.
    """

    def __init__(self):
        # Constantes físicas
        self.c = 299792.458  # Velocidad de la luz en km/s
        self.H0 = 70  # Constante de Hubble en km/s/Mpc (valor por defecto)
        self.G = 6.674e-11  # Constante gravitacional en m^3 kg^-1 s^-2

    def calcularHubble(self, velocidad: float, distancia: float) -> float:
        """
        Calcula la constante de Hubble a partir de velocidad y distancia.

        Args:
            velocidad: Velocidad de recesión en km/s
            distancia: Distancia en Megaparsecs (Mpc)

        Returns:
            Constante de Hubble en km/s/Mpc
        """
        if distancia == 0:
            raise ValueError("La distancia no puede ser cero")

        H = velocidad / distancia
        return H

    def calcularRedshift(self, longitud_observada: float, longitud_emitida: float) -> float:
        """
        Calcula el redshift (corrimiento al rojo) de una galaxia.

        Args:
            longitud_observada: Longitud de onda observada en nm
            longitud_emitida: Longitud de onda emitida en nm

        Returns:
            Redshift z (adimensional)
        """
        if longitud_emitida == 0:
            raise ValueError("La longitud emitida no puede ser cero")

        z = (longitud_observada - longitud_emitida) / longitud_emitida
        return z

    def calcularVelocidadAngular(self, velocidad_lineal: float, radio: float) -> float:
        """
        Calcula la velocidad angular de un objeto en órbita.

        Args:
            velocidad_lineal: Velocidad lineal en km/s
            radio: Radio de la órbita en km

        Returns:
            Velocidad angular en rad/s
        """
        if radio == 0:
            raise ValueError("El radio no puede ser cero")

        # Convertir km/s a m/s para mayor precisión
        v_ms = velocidad_lineal * 1000
        r_m = radio * 1000

        omega = v_ms / r_m
        return omega

    def calcularOrbita(self, masa_central: float, radio: float) -> Tuple[float, float]:
        """
        Calcula la velocidad orbital y el período de un objeto en órbita circular.

        Args:
            masa_central: Masa del objeto central en kg
            radio: Radio de la órbita en metros

        Returns:
            Tupla (velocidad_orbital en m/s, periodo en segundos)
        """
        if radio <= 0 or masa_central <= 0:
            raise ValueError("La masa y el radio deben ser positivos")

        # Velocidad orbital: v = sqrt(GM/r)
        v_orbital = np.sqrt(self.G * masa_central / radio)

        # Período orbital: T = 2πr/v
        periodo = 2 * np.pi * radio / v_orbital

        return v_orbital, periodo

    def calcularDistanciaHubble(self, redshift: float) -> float:
        """
        Calcula la distancia usando la ley de Hubble y el redshift.

        Args:
            redshift: Valor de z

        Returns:
            Distancia en Mpc
        """
        # Para z pequeños: v ≈ cz
        velocidad = self.c * redshift
        distancia = velocidad / self.H0

        return distancia

    def analizar_datos_csv(self, archivo_csv: str) -> pd.DataFrame:
        """
        Lee y analiza datos astronómicos desde un archivo CSV.

        Args:
            archivo_csv: Ruta al archivo CSV

        Returns:
            DataFrame con los resultados de los cálculos
        """
        df = pd.read_csv(archivo_csv)
        resultados = []

        for idx, row in df.iterrows():
            resultado = {
                'galaxia': row['galaxia'],
                'velocidad_km_s': row['velocidad'],
                'distancia_Mpc': row['distancia']
            }

            # Calcular constante de Hubble
            resultado['H0_calculado'] = self.calcularHubble(
                row['velocidad'],
                row['distancia']
            )

            # Si hay datos de redshift
            if 'longitud_obs' in row and 'longitud_emit' in row:
                resultado['redshift'] = self.calcularRedshift(
                    row['longitud_obs'],
                    row['longitud_emit']
                )
                resultado['distancia_via_redshift'] = self.calcularDistanciaHubble(
                    resultado['redshift']
                )

            resultados.append(resultado)

        return pd.DataFrame(resultados)
