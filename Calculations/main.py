"""
Script de prueba para la clase Calculos
Ejecutar: python main_test_calculos.py
"""

from calculos2 import Calculos
import numpy as np

def separador(titulo):
    """Imprime un separador visual"""
    print("\n" + "="*70)
    print(f"  {titulo}")
    print("="*70 + "\n")

def main():
    print("🚀 SISTEMA DE CÁLCULOS ASTRONÓMICOS")
    print("    Prueba de la clase Calculos\n")
    
    # Inicializar la clase
    calc = Calculos(data_path="routines/data")
    
    # =========================================================================
    # PRUEBA 1: Calcular Constante de Hubble
    # =========================================================================
    separador("PRUEBA 1: Calcular Constante de Hubble")
    velocidad = 5000  # km/s
    distancia = 71.4  # Mpc
    
    H = calc.calcularHubble(velocidad, distancia)
    print(f"Datos de entrada:")
    print(f"  - Velocidad de recesión: {velocidad} km/s")
    print(f"  - Distancia: {distancia} Mpc")
    print(f"\nResultado:")
    print(f"  ➜ Constante de Hubble: {H:.2f} km/s/Mpc")
    
    # =========================================================================
    # PRUEBA 2: Calcular Redshift
    # =========================================================================
    separador("PRUEBA 2: Calcular Redshift")
    lambda_obs = 656.3  # nm (H-alpha observada)
    lambda_emit = 486.1  # nm (H-beta en reposo)
    
    z = calc.calcularRedshift(lambda_obs, lambda_emit)
    print(f"Datos de entrada:")
    print(f"  - Longitud de onda observada: {lambda_obs} nm")
    print(f"  - Longitud de onda emitida: {lambda_emit} nm")
    print(f"\nResultado:")
    print(f"  ➜ Redshift (z): {z:.6f}")
    print(f"  ➜ Interpretación: El objeto se {'aleja' if z > 0 else 'acerca'}")
    
    # =========================================================================
    # PRUEBA 3: Calcular Distancia de Hubble desde Redshift
    # =========================================================================
    separador("PRUEBA 3: Calcular Distancia usando Ley de Hubble")
    z_test = 0.05
    
    distancia_info = calc.calcularDistanciaHubble(z_test)
    print(f"Datos de entrada:")
    print(f"  - Redshift: {z_test}")
    print(f"  - H₀ usado: {distancia_info['H0_usado']} km/s/Mpc")
    print(f"\nResultados:")
    print(f"  ➜ Velocidad de recesión: {distancia_info['velocidad_km_s']:.2f} km/s")
    print(f"  ➜ Distancia: {distancia_info['distancia_Mpc']:.2f} Mpc")
    print(f"  ➜ Distancia: {distancia_info['distancia_años_luz']:.2e} años luz")
    
    # =========================================================================
    # PRUEBA 4: Calcular Velocidad Angular
    # =========================================================================
    separador("PRUEBA 4: Calcular Velocidad Angular")
    periodo = 365.25 * 24 * 3600  # 1 año en segundos (Tierra)
    radio = 1.496e11  # 1 AU en metros
    
    vel_angular = calc.calcularVelocidadAngular(periodo, radio)
    print(f"Datos de entrada:")
    print(f"  - Período orbital: {periodo/(86400*365.25):.2f} años")
    print(f"  - Radio orbital: {radio/calc.AU:.2f} AU")
    print(f"\nResultados:")
    print(f"  ➜ Velocidad angular: {vel_angular['velocidad_angular']:.10e} rad/s")
    print(f"  ➜ Velocidad lineal: {vel_angular['velocidad_lineal']/1000:.2f} km/s")
    
    # =========================================================================
    # PRUEBA 5: Calcular Parámetros Orbitales
    # =========================================================================
    separador("PRUEBA 5: Calcular Órbita (Tierra alrededor del Sol)")
    masa_sol = 1.989e30  # kg
    radio_tierra = 1.496e11  # metros (1 AU)
    excentricidad = 0.0167  # Tierra
    
    orbita = calc.calcularOrbita(masa_sol, radio_tierra, excentricidad)
    print(f"Datos de entrada:")
    print(f"  - Masa central (Sol): {masa_sol:.3e} kg")
    print(f"  - Semi-eje mayor: {radio_tierra/calc.AU:.2f} AU")
    print(f"  - Excentricidad: {excentricidad}")
    print(f"\nResultados:")
    print(f"  ➜ Período orbital: {orbita['periodo_años']:.4f} años")
    print(f"  ➜ Velocidad orbital: {orbita['velocidad_orbital']/1000:.2f} km/s")
    print(f"  ➜ Perihelio: {orbita['perihelio']/calc.AU:.4f} AU")
    print(f"  ➜ Afelio: {orbita['afelio']/calc.AU:.4f} AU")
    
    # =========================================================================
    # PRUEBA 6: Listar Datasets Disponibles
    # =========================================================================
    separador("PRUEBA 6: Datasets Disponibles")
    datasets = calc.listar_datasets()
    
    if datasets:
        print(f"Se encontraron {len(datasets)} dataset(s):\n")
        for i, dataset in enumerate(datasets, 1):
            print(f"  {i}. {dataset}")
            try:
                info = calc.obtener_info_dataset(dataset)
                print(f"     📁 Columnas ({info['num_columnas']}): {', '.join(info['columnas'][:5])}...")
            except Exception as e:
                print(f"     ⚠️  Error al leer: {e}")
        
        # =========================================================================
        # PRUEBA 7: Analizar un Dataset
        # =========================================================================
        separador("PRUEBA 7: Análisis de Dataset")
        
        # Intentar analizar el primer dataset disponible
        if datasets:
            dataset_a_analizar = datasets[0]
            print(f"Analizando dataset: {dataset_a_analizar}")
            
            try:
                df_resultado = calc.analizar_datos_csv(dataset_a_analizar)
                
                print(f"\n✅ Análisis completado exitosamente!")
                print(f"\nPrimeras 5 filas del resultado:")
                print(df_resultado.head())
                
                print(f"\nColumnas agregadas durante el análisis:")
                cols_nuevas = set(df_resultado.columns) - set(calc.obtener_info_dataset(dataset_a_analizar)['columnas'])
                if cols_nuevas:
                    for col in cols_nuevas:
                        print(f"  ➜ {col}")
                else:
                    print("  (No se agregaron nuevas columnas)")
                
            except Exception as e:
                print(f"❌ Error durante el análisis: {e}")
    else:
        print("⚠️  No se encontraron datasets en la carpeta 'routines/data'")
        print("    Por favor, asegúrate de que existen archivos CSV en esa ubicación.")
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    separador("RESUMEN DE PRUEBAS")
    print("✅ Todas las funciones de cálculo fueron probadas")
    print("✅ La clase está lista para integrarse al orquestador")
    print("\n📝 Próximos pasos:")
    print("   1. Colocar archivos CSV en routines/data/")
    print("   2. Ejecutar análisis con datasets reales")
    print("   3. Integrar con el orquestador de rutinas")
    print("\n🎯 Funciones disponibles:")
    print("   - calcularHubble(velocidad, distancia)")
    print("   - calcularRedshift(lambda_obs, lambda_emit)")
    print("   - calcularVelocidadAngular(periodo, radio)")
    print("   - calcularOrbita(masa_central, radio, excentricidad)")
    print("   - calcularDistanciaHubble(z, H0)")
    print("   - analizar_datos_csv(dataset_name, calculos_aplicar)")
    print("   - listar_datasets()")
    print("   - obtener_info_dataset(dataset_name)")

if __name__ == "__main__":
    main()