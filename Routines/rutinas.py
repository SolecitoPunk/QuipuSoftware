import pandas as pd
from typing import Optional, Dict, List
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar desde la carpeta DB
from DB.entrada import Entrada
from DB.BaseDatos import BaseDatos

# Importar la clase Calculos
from Calculations.calculos import Calculos

class Rutina:
    """Orquestador central del sistema de análisis astronómico.
    
    Coordina la carga de datos (locales o remotos), su procesamiento,
    cálculos científicos y generación de salidas educativas.
    """
    
    def __init__(self):
        """Inicializa los componentes del sistema."""
        self.entrada = Entrada()
        self.base_datos = BaseDatos()
        self.calculos = Calculos(data_path="routines/data")  # 🆕 Integración de Calculos
        self.datos_actuales = None
        self.datos_procesados = None  # 🆕 Para guardar datos con cálculos
        self.fuente_actual = None
        self.metadatos = {}
    
    def menuPrincipal(self):
        """Muestra el menú principal de opciones."""
        print("\n" + "="*60)
        print("🌌 SISTEMA DE ANÁLISIS ASTRONÓMICO EDUCATIVO")
        print("="*60)
        print("\n📂 FUENTES DE DATOS:")
        print("  1. Archivos locales (CSV/DAT)")
        print("  2. SDSS - Galaxias y espectros")
        print("  3. DESI - Objetos del cosmos profundo")
        print("  4. NASA ESI - Exoplanetas")
        print("  5. NEO - Asteroides y cometas")
        print("\n🔬 ANÁLISIS Y CÁLCULOS:")
        print("  6. Ver datasets disponibles")
        print("  7. Analizar dataset guardado")
        print("  8. Ver último reporte")
        print("\n  0. Salir")
        print("-"*60)
    
    def cargarDatos(self, opcion: int) -> bool:
        """Carga datos según la opción seleccionada.
        
        Args:
            opcion: Número de la fuente seleccionada (1-5)
            
        Returns:
            True si la carga fue exitosa, False en caso contrario
        """
        if opcion == 1:
            print("\n📁 Cargando desde archivos locales...")
            self.datos_actuales = self.entrada.leerDatos()
            self.fuente_actual = "local"
            
        elif opcion in [2, 3, 4, 5]:
            fuentes = {2: "SDSS", 3: "DESI", 4: "NASA ESI", 5: "NEO"}
            fuente = fuentes[opcion]
            
            print(f"\n🌐 Consultando {fuente}...")
            
            # Solicitar parámetros según la fuente
            if fuente in ["SDSS", "DESI"]:
                try:
                    ra = float(input("Ingresa RA (grados, ej: 180.0): "))
                    dec = float(input("Ingresa DEC (grados, ej: 0.0): "))
                    z_min = float(input("Ingresa z-min (ej: 0.05): "))
                    z_max = float(input("Ingresa z-max (ej: 0.3): "))
                    
                    resultado = self.base_datos.conectar(
                        ra=ra, dec=dec, z_min=z_min, z_max=z_max, source=fuente
                    )
                except ValueError:
                    print("❌ Error: Valores inválidos")
                    return False
            else:
                # NASA ESI y NEO no necesitan todos los parámetros
                resultado = self.base_datos.conectar(source=fuente)
            
            if resultado is not None:
                # Guardar y convertir a DataFrame
                archivo_guardado = self.base_datos.guardardatos(resultado, fuente)
                
                if hasattr(resultado, 'to_pandas'):
                    self.datos_actuales = resultado.to_pandas()
                else:
                    self.datos_actuales = resultado
                
                self.fuente_actual = fuente
                self.metadatos['archivo'] = archivo_guardado
                
                print(f"✓ Datos guardados en: {archivo_guardado}")
                if self.fuente_actual == "DESI":
                    print("\n🌌 Calculando Photoz automáticamente para DESI...")
                    if self.aplicarCalculos(calculos_aplicar=["photoz"]):
                        self.datos_actuales = self.datos_procesados
                        print("✓ Photoz calculado y datos actualizados.")
            else:
                print("❌ No se obtuvieron datos de la fuente")
                return False
        else:
            return False
        
        return self.datos_actuales is not None
    
    def procesarDatos(self):
        """Procesa y valida los datos cargados."""
        if self.datos_actuales is None:
            print("⚠️  No hay datos cargados")
            return False
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE DATOS")
        print("="*60)
        print(f"Fuente: {self.fuente_actual}")
        print(f"Registros: {len(self.datos_actuales)}")
        print(f"Columnas: {len(self.datos_actuales.columns)}")
        print(f"\n📋 Columnas disponibles:")
        for i, col in enumerate(self.datos_actuales.columns, 1):
            print(f"  {i}. {col}")
        
        print(f"\n🔍 Primeras 3 filas:")
        print(self.datos_actuales.head(3))
        
        # Estadísticas básicas solo para columnas numéricas
        columnas_numericas = self.datos_actuales.select_dtypes(include=['number']).columns
        if len(columnas_numericas) > 0:
            print(f"\n📈 Estadísticas básicas (columnas numéricas):")
            print(self.datos_actuales[columnas_numericas].describe())
        
        return True
    
    def aplicarCalculos(self, calculos_aplicar: Optional[List[str]] = None) -> bool:
        """🆕 Aplica cálculos astronómicos a los datos actuales."""
        if self.datos_actuales is None:
            print("⚠️  No hay datos cargados para analizar")
            return False
        
        print("\n" + "="*60)
        print("🔬 APLICANDO CÁLCULOS ASTRONÓMICOS")
        print("="*60)
        
        try:
            # Aplicar análisis usando la clase Calculos
            self.datos_procesados = self.calculos.analizar_datos_csv(
                df=self.datos_actuales,
                fuente=self.fuente_actual,
                calculos_aplicar=calculos_aplicar
            )
            
            print("\n✅ Cálculos aplicados exitosamente")
            
            # Mostrar columnas nuevas agregadas
            columnas_originales = set(self.datos_actuales.columns)
            columnas_nuevas = set(self.datos_procesados.columns) - columnas_originales
            
            if columnas_nuevas:
                print(f"\n📊 Nuevas columnas calculadas:")
                for col in columnas_nuevas:
                    print(f"   • {col}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al aplicar cálculos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verReporte(self):
        """🆕 Muestra el reporte del último análisis."""
        reporte = self.calculos.generar_reporte()
        print(reporte)
    
    def listarDatasetsDisponibles(self):
        """🆕 Lista los datasets disponibles en routines/data."""
        print("\n" + "="*60)
        print("📚 DATASETS DISPONIBLES")
        print("="*60)
        
        datasets = self.calculos.listar_datasets()
        
        if not datasets:
            print("⚠️  No hay datasets en la carpeta 'routines/data'")
            print("   Carga datos desde las opciones 2-5 para crear datasets")
            return
        
        for i, dataset in enumerate(datasets, 1):
            try:
                info = self.calculos.obtener_info_dataset(dataset)
                print(f"\n{i}. {dataset}")
                print(f"   📁 Ruta: {info['ruta']}")
                print(f"   📊 Columnas ({info['num_columnas']}): {', '.join(info['columnas'][:5])}...")
            except Exception as e:
                print(f"\n{i}. {dataset}")
                print(f"   ⚠️  Error al leer: {e}")
    
    def analizarDatasetGuardado(self):
        """🆕 Analiza un dataset previamente guardado."""
        datasets = self.calculos.listar_datasets()
        
        if not datasets:
            print("\n⚠️  No hay datasets disponibles para analizar")
            return False
        
        print("\n" + "="*60)
        print("📊 SELECCIONAR DATASET PARA ANALIZAR")
        print("="*60)
        
        for i, dataset in enumerate(datasets, 1):
            print(f"  {i}. {dataset}")
        
        try:
            seleccion = int(input(f"\nSeleccione dataset (1-{len(datasets)}): "))
            
            if 1 <= seleccion <= len(datasets):
                dataset_nombre = datasets[seleccion - 1]
                
                print(f"\n🔍 Analizando {dataset_nombre}...")
                
                # Analizar dataset
                self.datos_procesados = self.calculos.analizar_datos_csv(
                    dataset_name=dataset_nombre
                )
                
                print("\n✅ Análisis completado")
                
                # Preguntar si desea ver el reporte
                ver = input("\n¿Desea ver el reporte completo? (s/n): ").lower()
                if ver == 's':
                    self.verReporte()
                
                # Preguntar si desea guardar resultados
                guardar = input("\n¿Desea guardar los resultados con cálculos? (s/n): ").lower()
                if guardar == 's':
                    nombre_salida = f"{dataset_nombre}_calculado.csv"
                    ruta_salida = self.calculos.data_path / nombre_salida
                    self.datos_procesados.to_csv(ruta_salida, index=False)
                    print(f"✓ Resultados guardados en: {ruta_salida}")
                
                return True
            else:
                print("❌ Selección inválida")
                return False
                
        except ValueError:
            print("❌ Debe ingresar un número")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def enviarCalculos(self) -> Dict:
        """Prepara los datos para enviar al módulo de Cálculos.
        
        Returns:
            Diccionario con datos y metadatos preparados
        """
        if self.datos_actuales is None:
            return {}
        
        paquete = {
            'datos': self.datos_actuales,
            'datos_procesados': self.datos_procesados,
            'fuente': self.fuente_actual,
            'columnas': list(self.datos_actuales.columns),
            'n_registros': len(self.datos_actuales),
            'metadatos': self.metadatos,
            'tiene_calculos': self.datos_procesados is not None
        }
        
        return paquete
    def menu_calculos(self):
        """Muestra el menú de cálculos astronómicos según la fuente de datos."""
        calculos_disponibles = {
            "NASA ESI": ["Calcular órbitas", "Calcular velocidades"],
            "DESI": ["Calcular distancia de Hubble", "Calcular constante de Hubble"],
            "SDSS": ["Calcular distancia de Hubble", "Calcular constante de Hubble"],
            "NEO": ["Calcular órbitas"],
            "local": []
        }

        fuente = self.fuente_actual
        if fuente not in calculos_disponibles:
            print("No hay cálculos disponibles para esta fuente de datos.")
            return

        opciones = calculos_disponibles[fuente]
        if not opciones:
            print("No hay cálculos disponibles para archivos locales.")
            return

        while True:
            print("\n" + "="*60)
            print(f"🔬 CÁLCULOS DISPONIBLES PARA {fuente}")
            print("="*60)
            for i, opcion in enumerate(opciones, 1):
                print(f"{i}. {opcion}")
            print("0. Volver al menú de análisis")
            print("-"*60)

            seleccion = input(f"Seleccione un cálculo (1-{len(opciones)}): ")

            try:
                seleccion = int(seleccion)
                if 0 < seleccion <= len(opciones):
                    calculo_seleccionado = opciones[seleccion - 1]
                    print(f"\nEjecutando '{calculo_seleccionado}'...")
                    if self.aplicarCalculos(calculos_aplicar=[calculo_seleccionado]):
                        self.verReporte()
                        guardar = input("\n💾 ¿Guardar resultados con cálculos? (s/n): ").lower()
                        if guardar == 's':
                            nombre_salida = f"{self.fuente_actual}_analisis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
                            ruta_salida = self.calculos.data_path / nombre_salida
                            self.datos_procesados.to_csv(ruta_salida, index=False)
                            print(f"✓ Guardado en: {ruta_salida}")
                elif seleccion == 0:
                    break
                else:
                    print("Selección no válida.")
            except ValueError:
                print("Debe ingresar un número.")

    def menu_analisis(self):
        """Muestra el menú de análisis y maneja la selección del usuario."""
        while True:
            print("\n" + "="*60)
            print("🔬 MENÚ DE ANÁLISIS")
            print("="*60)
            print("1. Realizar cálculos astronómicos")
            print("2. Usar herramientas de Machine Learning")
            print("0. Volver al menú principal")
            print("-"*60)

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                self.menu_calculos()
            elif opcion == "2":
                print("\n--- Lanzando Módulo de Machine Learning ---")
                try:
                    from ML.MachineL import MenuML
                    menu_ml = MenuML()
                    menu_ml.mostrar_menu()
                except Exception as e:
                    print(f"ERROR al ejecutar el módulo de Machine Learning: {e}")
                print("--- Módulo de Machine Learning Finalizado ---")
            elif opcion == "0":
                break
            else:
                print("Opción no válida. Por favor, intente de nuevo.")
    def ejecutar(self):
        """Ejecuta el flujo principal del sistema."""
        print("\n🚀 Inicializando sistema...")
        print(f"✓ Módulo de Entrada: OK")
        print(f"✓ Base de Datos: OK")
        print(f"✓ Módulo de Cálculos: OK")
        
        while True:
            self.menuPrincipal()
            
            try:
                opcion = int(input("\nSeleccione una opción (0-8): "))
                
                if opcion == 0:
                    print("\n👋 ¡Hasta pronto!")
                    print("   Gracias por usar el Sistema de Análisis Astronómico")
                    break
                
                # Cargar datos de fuentes remotas o locales
                if 1 <= opcion <= 5:
                    exito = self.cargarDatos(opcion)
                    
                    if exito:
                        self.procesarDatos()
                        self.menu_analisis()
                    else:
                        print("❌ No se pudieron cargar los datos")
                
                # Ver datasets disponibles
                elif opcion == 6:
                    self.listarDatasetsDisponibles()
                
                # Analizar dataset guardado
                elif opcion == 7:
                    self.analizarDatasetGuardado()
                
                # Ver último reporte
                elif opcion == 8:
                    self.verReporte()
                
                else:
                    print("❌ Opción no válida")
                    
            except ValueError:
                print("❌ Debe ingresar un número")
            except KeyboardInterrupt:
                print("\n\n👋 Operación cancelada por el usuario")
                continuar = input("¿Desea salir del sistema? (s/n): ").lower()
                if continuar == 's':
                    break
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                print("   El sistema continuará ejecutándose...")


def main():
    """Función principal para ejecutar el sistema."""
    sistema = Rutina()
    sistema.ejecutar()


if __name__ == "__main__":
    main()
