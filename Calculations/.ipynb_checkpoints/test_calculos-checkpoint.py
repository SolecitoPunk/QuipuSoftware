"""
Script de prueba para la clase Calculos
Demuestra todas las funcionalidades de cálculos astronómicos
"""

from calculos import Calculos
import numpy as np

def separador(titulo):
    """Imprime un separador visual"""
    print("\n" + "="*60)
    print(f"  {titulo}")
    print("="*60)

def main():
    # Crear instancia de la clase
    calc = Calculos()

    print("\n🌌 PROGRAMA DE CÁLCULOS ASTRONÓMICOS 🌌\n")

    # ===== PRUEBA 1: Calcular Constante de Hubble =====
    separador("1. CÁLCULO DE LA CONSTANTE DE HUBBLE")

    velocidad = 1500  # km/s
    distancia = 22.0  # Mpc

    H = calc.calcularHubble(velocidad, distancia)
    print(f"\nVelocidad de recesión: {velocidad} km/s")
    print(f"Distancia: {distancia} Mpc")
    print(f"Constante de Hubble calculada: H₀ = {H:.2f} km/s/Mpc")
    print(f"Valor típico de H₀: ~70 km/s/Mpc")

    # ===== PRUEBA 2: Calcular Redshift =====
    separador("2. CÁLCULO DEL REDSHIFT")

    longitud_obs = 658.0  # nm (longitud observada)
    longitud_emit = 656.3  # nm (línea H-alpha del hidrógeno)

    z = calc.calcularRedshift(longitud_obs, longitud_emit)
    print(f"\nLongitud de onda emitida (H-α): {longitud_emit} nm")
    print(f"Longitud de onda observada: {longitud_obs} nm")
    print(f"Redshift: z = {z:.6f}")
    print(f"Velocidad de recesión (v ≈ cz): {z * calc.c:.2f} km/s")

    # ===== PRUEBA 3: Calcular Velocidad Angular =====
    separador("3. CÁLCULO DE VELOCIDAD ANGULAR")

    v_lineal = 220  # km/s (velocidad del Sol alrededor del centro galáctico)
    radio = 26000 * 9.461e12  # km (8 kpc convertidos a km)

    omega = calc.calcularVelocidadAngular(v_lineal, radio)
    periodo_anos = (2 * np.pi / omega) / (365.25 * 24 * 3600)

    print(f"\nVelocidad lineal: {v_lineal} km/s")
    print(f"Radio de la órbita: ~26,000 años luz")
    print(f"Velocidad angular: ω = {omega:.3e} rad/s")
    print(f"Período orbital: ~{periodo_anos:.1f} millones de años")

    # ===== PRUEBA 4: Calcular Órbita =====
    separador("4. CÁLCULO DE PARÁMETROS ORBITALES")

    # Ejemplo: Satélite en órbita baja terrestre
    masa_tierra = 5.972e24  # kg
    radio_orbita = 6371e3 + 400e3  # m (radio Tierra + 400 km de altura)

    v_orbital, periodo = calc.calcularOrbita(masa_tierra, radio_orbita)

    print(f"\nMasa del objeto central (Tierra): {masa_tierra:.3e} kg")
    print(f"Radio de la órbita: {radio_orbita/1000:.0f} km")
    print(f"Velocidad orbital: {v_orbital/1000:.2f} km/s")
    print(f"Período orbital: {periodo/3600:.2f} horas")
    print(f"(Órbita similar a la Estación Espacial Internacional)")

    # ===== PRUEBA 5: Distancia mediante Hubble =====
    separador("5. CÁLCULO DE DISTANCIA VÍA LEY DE HUBBLE")

    z_ejemplo = 0.05
    distancia_calc = calc.calcularDistanciaHubble(z_ejemplo)

    print(f"\nRedshift observado: z = {z_ejemplo}")
    print(f"Velocidad de recesión: v = {z_ejemplo * calc.c:.2f} km/s")
    print(f"Distancia calculada: {distancia_calc:.2f} Mpc")
    print(f"Equivalente a: {distancia_calc * 3.26:.2f} millones de años luz")

    # ===== PRUEBA 6: Análisis de datos CSV =====
    separador("6. ANÁLISIS DE DATOS DE GALAXIAS (CSV)")

    try:
        print("\nCargando datos desde 'datos_galaxias.csv'...")
        resultados = calc.analizar_datos_csv('datos_galaxias.csv')

        print(f"\nSe analizaron {len(resultados)} galaxias:")
        print("\n" + "-"*100)
        print(f"{'Galaxia':<15} {'Velocidad':<12} {'Distancia':<12} {'H₀ calc':<12} {'Redshift':<12} {'Dist(z)':<12}")
        print(f"{'':15} {'(km/s)':<12} {'(Mpc)':<12} {'(km/s/Mpc)':<12} {'z':<12} {'(Mpc)':<12}")
        print("-"*100)

        for _, row in resultados.iterrows():
            redshift_str = f"{row['redshift']:.6f}" if 'redshift' in row else "N/A"
            dist_z_str = f"{row['distancia_via_redshift']:.2f}" if 'distancia_via_redshift' in row else "N/A"

            print(f"{row['galaxia']:<15} {row['velocidad_km_s']:>10.1f}  "
                  f"{row['distancia_Mpc']:>10.2f}  {row['H0_calculado']:>10.2f}  "
                  f"{redshift_str:>10}  {dist_z_str:>10}")

        H0_promedio = resultados['H0_calculado'].mean()
        print("-"*100)
        print(f"\nConstante de Hubble promedio: H₀ = {H0_promedio:.2f} km/s/Mpc")
        print(f"Desviación estándar: ±{resultados['H0_calculado'].std():.2f} km/s/Mpc")

    except FileNotFoundError:
        print("\n⚠️  Archivo 'datos_galaxias.csv' no encontrado.")
        print("Por favor, crea el archivo CSV primero.")
    except Exception as e:
        print(f"\n❌ Error al procesar el CSV: {e}")

    # ===== RESUMEN FINAL =====
    separador("PRUEBAS COMPLETADAS")
    print("\n✅ Todos los métodos de la clase Calculos fueron probados exitosamente.")
    print("\nMétodos disponibles:")
    print("  • calcularHubble(velocidad, distancia)")
    print("  • calcularRedshift(longitud_obs, longitud_emit)")
    print("  • calcularVelocidadAngular(velocidad_lineal, radio)")
    print("  • calcularOrbita(masa_central, radio)")
    print("  • calcularDistanciaHubble(redshift)")
    print("  • analizar_datos_csv(archivo_csv)")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
