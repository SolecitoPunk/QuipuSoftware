import pandas as pd
from typing import Optional, Dict
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar desde las carpetas DB, Calculations y ML
from DB.entrada import Entrada
from DB.BaseDatos import BaseDatos
from Calculations.Calculations import MenuCalculos
from ML.MachineL import MenuML

class Rutina:
    """Orquestador central del sistema de análisis astronómico.
    
    Coordina la carga de datos (locales o remotos), su procesamiento,
    cálculos científicos y generación de salidas educativas.
    """
    
    def __init__(self):
        """Inicializa los componentes del sistema."""
        self.entrada = Entrada()
        self.base_datos = BaseDatos()
        self.menu_calculos = MenuCalculos()
        self.menu_ml = MenuML()
        self.datos_actuales = None
        self.fuente_actual = None
        self.metadatos = {}
    
    def menuPrincipal(self):
        """Muestra el menú principal de opciones."""
        print("\n" + "="*50)
        print("🌌 SISTEMA DE ANÁLISIS ASTRONÓMICO EDUCATIVO")
        print("="*50)
        print("\n📂 FUENTES DE DATOS:")
        print("  1. Archivos locales (CSV/DAT)")
        print("  2. SDSS - Galaxias y espectros")
        print("  3. DESI - Objetos del cosmos profundo")
        print("  4. NASA ESI - Exoplanetas")
        print("  5. NEO - Asteroides y cometas")
        print("\n  0. Salir")
        print("-"*50)
    
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
                ra = float(input("Ingresa RA (grados, ej: 180.0): "))
                dec = float(input("Ingresa DEC (grados, ej: 0.0): "))
                z_min = float(input("Ingresa z-min (ej: 0.05): "))
                z_max = float(input("Ingresa z-max (ej: 0.3): "))
                
                resultado = self.base_datos.conectar(
                    ra=ra, dec=dec, z_min=z_min, z_max=z_max, source=fuente
                )
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
            else:
                return False
        else:
            return False
        
        return self.datos_actuales is not None
    
    def procesarDatos(self):
        """Procesa y valida los datos cargados."""
        if self.datos_actuales is None:
            print("⚠️  No hay datos cargados")
            return False
        
        print("\n" + "="*50)
        print("📊 RESUMEN DE DATOS")
        print("="*50)
        print(f"Fuente: {self.fuente_actual}")
        print(f"Registros: {len(self.datos_actuales)}")
        print(f"Columnas: {len(self.datos_actuales.columns)}")
        print(f"\nColumnas disponibles:")
        for i, col in enumerate(self.datos_actuales.columns, 1):
            print(f"  {i}. {col}")
        
        print(f"\n📋 Primeras filas:")
        print(self.datos_actuales.head())
        
        print(f"\n📈 Estadísticas básicas:")
        print(self.datos_actuales.describe())
        
        return True
    
    def enviarCalculos(self) -> Dict:
        """Prepara los datos para enviar al módulo de Cálculos.
        
        Returns:
            Diccionario con datos y metadatos preparados
        """
        if self.datos_actuales is None:
            return {}
        
        paquete = {
            'datos': self.datos_actuales,
            'fuente': self.fuente_actual,
            'columnas': list(self.datos_actuales.columns),
            'n_registros': len(self.datos_actuales),
            'metadatos': self.metadatos
        }
        
        return paquete
    
    def menuPostCarga(self):
        """Muestra el menú de acciones después de cargar los datos."""
        while True:
            print("\n" + "="*50)
            print("🔬 ¿QUÉ DESEA HACER CON LOS DATOS CARGADOS?")
            print("="*50)
            print("  1. Realizar Cálculos Astronómicos")
            print("  2. Utilizar Herramientas de Machine Learning")
            print("  3. Cargar un nuevo set de datos")
            print("\n  0. Salir al menú principal")
            print("-"*50)

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                print("\n🔭 Accediendo al módulo de Cálculos...")
                self.menu_calculos.mostrar_menu(self.datos_actuales)
            elif opcion == "2":
                print("\n🤖 Accediendo al módulo de Machine Learning...")
                self.menu_ml.mostrar_menu(self.datos_actuales)
            elif opcion == "3":
                break # Sale del bucle para volver al menú de carga
            elif opcion == "0":
                return "salir" # Señal para salir del programa principal
            else:
                print("✗ Opción no válida.")
        return None

    def ejecutar(self):
        """Ejecuta el flujo principal del sistema."""
        while True:
            self.menuPrincipal()
            
            try:
                opcion = int(input("\nSeleccione una opción (0-5): "))
                
                if opcion == 0:
                    print("\n👋 ¡Hasta pronto!")
                    break
                
                if 1 <= opcion <= 5:
                    if self.cargarDatos(opcion):
                        self.procesarDatos()
                        
                        # Mostrar menú post-carga
                        if self.menuPostCarga() == "salir":
                            print("\n👋 ¡Hasta pronto!")
                            break
                    else:
                        print("✗ No se pudieron cargar los datos. Volviendo al menú principal.")
                else:
                    print("✗ Opción no válida.")
                    
            except (ValueError, KeyboardInterrupt):
                print("\n\n👋 Operación cancelada. Volviendo al menú principal.")
            except Exception as e:
                print(f"✗ Error inesperado: {e}")


if __name__ == "__main__":
    sistema = Rutina()
    sistema.ejecutar()
