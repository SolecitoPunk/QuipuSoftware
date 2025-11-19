from typing import Optional
import pandas as pd
import os

class Entrada:
    """Clase para manejar la entrada de datos desde archivos en la carpeta 'data'."""
    
    def __init__(self):
        self.archivo = None

    def seleccionarArchivo(self) -> Optional[str]:
        """Busca los archivos en la carpeta 'data' y permite al usuario seleccionar uno."""
        carpeta_data = os.path.join(os.path.dirname(__file__), "data")

        # Verificar si la carpeta existe
        if not os.path.exists(carpeta_data):
            print("✗ No se encontró la carpeta 'data'. Creándola...")
            os.makedirs(carpeta_data)
            return None

        # Listar archivos .csv y .dat
        archivos = [f for f in os.listdir(carpeta_data) if f.endswith(('.csv', '.dat'))]

        if not archivos:
            print("✗ No se encontraron archivos .csv o .dat en la carpeta 'data'.")
            return None

        # Mostrar lista numerada
        print("\n📂 Archivos disponibles en 'data/':")
        for i, archivo in enumerate(archivos, 1):
            print(f"  {i}. {archivo}")

        # Selección del usuario
        try:
            opcion = int(input("\nSeleccione el número del archivo que desea leer: "))
            if 1 <= opcion <= len(archivos):
                archivo_seleccionado = os.path.join(carpeta_data, archivos[opcion - 1])
                print(f"✓ Archivo seleccionado: {archivos[opcion - 1]}")
                return archivo_seleccionado
            else:
                print("✗ Opción fuera de rango.")
                return None
        except ValueError:
            print("✗ Entrada no válida. Debe ser un número.")
            return None

    def leerDatos(self) -> Optional[pd.DataFrame]:
        """Lee los datos del archivo seleccionado usando pandas."""
        if not self.archivo:
            self.archivo = self.seleccionarArchivo()
            if not self.archivo:
                return None

        try:
            # Detectar formato y delimitador
            if self.archivo.endswith(".csv"):
                df = pd.read_csv(self.archivo)
            else:
                # Detectar delimitador común (tab o espacio)
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    primera_linea = f.readline()
                if '\t' in primera_linea:
                    df = pd.read_csv(self.archivo, sep='\t')
                else:
                    df = pd.read_csv(self.archivo, delim_whitespace=True)
            
            print(f"✓ Datos leídos correctamente: {len(df)} registros y {len(df.columns)} columnas.")
            return df
        
        except FileNotFoundError:
            print(f"✗ Error: Archivo '{self.archivo}' no encontrado")
        except Exception as e:
            print(f"✗ Error al leer datos: {str(e)}")
        return None


# Ejemplo de uso
if __name__ == "__main__":
    entrada = Entrada()
    df = entrada.leerDatos()
    if df is not None:
        print("\nPrimeras filas del archivo:")
        print(df.head())

