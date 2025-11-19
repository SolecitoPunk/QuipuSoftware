import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, HDBSCAN
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
import sys

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AnalisisDatos:
    """
    Clase para manejar la carga de datos a través del módulo de rutinas,
    aplicar K-Means clustering y visualizar los resultados.
    """
    def __init__(self):
        """
        Inicializa la clase sin una ruta de archivo fija.
        """
        self.df = None
        self.columnas_disponibles = []
        self.X_scaled = None
        self.labels = None
        self.columnas_elegidas = []

    def set_datos(self, dataframe):
        """
        Establece el dataframe de datos desde una fuente externa.
        """
        if dataframe is not None and not dataframe.empty:
            self.df = dataframe
            self.columnas_disponibles = self.df.select_dtypes(include=np.number).columns.tolist()
            print("\nDatos externos cargados en el módulo de Clustering.")
        else:
            print("ADVERTENCIA: Se intentó cargar un dataframe vacío o nulo.")

    def cargar_datos(self):
        """
        Verifica si los datos ya están cargados. Si no, instruye al usuario.
        """
        if self.df is not None:
            print("Utilizando datos ya cargados.")
            return True
        else:
            print("\nNo hay datos cargados. Por favor, cargue datos desde el menú principal.")
            return False

    def seleccionar_columnas(self):
        """
        Permite al usuario seleccionar dos columnas (Y y X) por su índice numérico.
        """
        if not self.df.empty and self.columnas_disponibles:
            print("\nColumnas numéricas disponibles para selección:")
            for i, col in enumerate(self.columnas_disponibles):
                print(f"  {i+1}. {col}")

            try:
                # Eje Y (primera columna a elegir)
                indice_y = int(input("Ingrese el número de la columna para el Eje Y: ")) - 1
                if 0 <= indice_y < len(self.columnas_disponibles):
                    col_y = self.columnas_disponibles[indice_y]
                else:
                    print("Selección de Eje Y no válida.")
                    return False

                # Eje X (segunda columna a elegir)
                indice_x = int(input("Ingrese el número de la columna para el Eje X: ")) - 1
                if 0 <= indice_x < len(self.columnas_disponibles) and indice_x != indice_y:
                    col_x = self.columnas_disponibles[indice_x]
                else:
                    if indice_x == indice_y:
                        print("Las columnas para X e Y deben ser diferentes.")
                    else:
                        print("Selección de Eje X no válida.")
                    return False

                # Las variables elegidas (X e Y)
                self.columnas_elegidas = [col_x, col_y]
                
                # Preprocesamiento y escalado de los datos seleccionados
                X = self.df[self.columnas_elegidas].values
                scaler = StandardScaler()
                self.X_scaled = scaler.fit_transform(X)

                print(f"\nColumnas seleccionadas: Eje Y ({col_y}), Eje X ({col_x}).")
                return True

            except ValueError:
                print("Entrada no válida. Debe ingresar un número.")
                return False
        else:
            print("ERROR: No hay datos cargados o columnas numéricas disponibles.")
            return False

    def aplicar_clustering(self):
        """
        Aplica el algoritmo de clustering seleccionado (K-Means o HDBSCAN) a las variables seleccionadas.
        """
        if self.X_scaled is not None:
            print("\nSeleccione el algoritmo de clustering:")
            print("1. K-Means")
            print("2. HDBSCAN")
            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                try:
                    n_clusters = int(input("Ingrese el número de clusters (k) a aplicar (e.g., 3): "))
                    if n_clusters <= 1:
                         print("El número de clusters debe ser mayor a 1.")
                         return False

                    # Aplicar K-Means
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                    self.labels = kmeans.fit_predict(self.X_scaled)
                    self.centroides = kmeans.cluster_centers_ # Guardar centroides (escalados)

                    print(f"Clustering K-Means aplicado con {n_clusters} clusters.")
                    return True
                except ValueError:
                    print("Entrada no válida. Debe ingresar un número entero para k.")
                    return False
                except Exception as e:
                    print(f"ERROR al aplicar K-Means: {e}")
                    return False

            elif opcion == "2":
                try:
                    # Aplicar HDBSCAN
                    hdbscan_clusterer = HDBSCAN(min_cluster_size=5, gen_min_span_tree=True)
                    self.labels = hdbscan_clusterer.fit_predict(self.X_scaled)

                    print(f"Clustering HDBSCAN aplicado.")
                    return True
                except Exception as e:
                    print(f"ERROR al aplicar HDBSCAN: {e}")
                    return False
            else:
                print("Opción no válida.")
                return False
        else:
            print("ERROR: Primero debe seleccionar y escalar las columnas.")
            return False

    def graficar_clusters(self):
        """
        Genera una gráfica de dispersión con Matplotlib de los clusters encontrados.
        """
        if self.X_scaled is not None and self.labels is not None:
            col_x = self.columnas_elegidas[0]
            col_y = self.columnas_elegidas[1]
            
            # Usamos los datos originales (no escalados) para la gráfica para mejor interpretación
            X_original = self.df[self.columnas_elegidas].values

            plt.figure(figsize=(10, 6))
            
            # Graficar los puntos de datos, coloreados por su cluster asignado
            scatter = plt.scatter(
                X_original[:, 0], # Eje X (primera columna elegida)
                X_original[:, 1], # Eje Y (segunda columna elegida)
                c=self.labels, 
                cmap='viridis', 
                marker='o', 
                alpha=0.6,
                edgecolor='k'
            )

            # Opcional: Graficar los centroides (tendrían que ser re-escalados si se quiere en el plot original, 
            # pero por simplicidad se omiten aquí, aunque los puedes calcular si deseas)
            # En un análisis real, se desescalarían los centroides para plotearlos junto a los datos originales.

            plt.title(f'Clusters K-Means en {col_y} vs {col_x}')
            plt.xlabel(col_x)
            plt.ylabel(col_y)
            plt.colorbar(scatter, label='Cluster ID')
            plt.grid(True)
            plt.savefig('cluster_plot.png')
            plt.show()
            print("Gráfica generada y guardada como 'cluster_plot.png'.")

        else:
            print("ERROR: Primero debe cargar datos, seleccionar columnas y aplicar clustering.")


    def menu(self):
        """
        Menú principal para interactuar con las funciones de análisis de datos.
        """
        if not self.cargar_datos():
            print("No se puede iniciar el menú sin cargar datos exitosamente.")
            return

        while True:
            print("\n--- Menú Análisis de Datos y Clustering ---")
            print("1. Seleccionar columnas (Y y X)")
            print("2. Aplicar Clustering (K-Means o HDBSCAN)")
            print("3. Generar Gráfica de Clusters")
            print("0. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                self.seleccionar_columnas()
            elif opcion == "2":
                self.aplicar_clustering()
            elif opcion == "3":
                self.graficar_clusters()
            elif opcion == "0":
                print("Saliendo del módulo de análisis.")
                break
            else:
                print("Opción no válida.")

# --- Código para Ejecutar el Módulo ---
if __name__ == "__main__":
    # Ahora la carga de datos se gestiona a través del menú interactivo de Rutina
    analizador = AnalisisDatos()
    analizador.menu()
