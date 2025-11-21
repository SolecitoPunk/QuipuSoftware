from .Cluster import AnalisisDatos
from .NN import AnalisisRegresionNN

class MenuML:
    """
    Una clase para mostrar un menú y lanzar los módulos de Machine Learning.
    """
    def mostrar_menu(self):
        """
        Muestra el menú principal de Machine Learning y maneja la selección del usuario.
        """
        while True:
            print("\n--- Menú Principal de Machine Learning ---")
            print("1. Módulo de Clustering")
            print("2. Módulo de Regresión con Red Neuronal")
            print("0. Salir")

            opcion = input("Seleccione un módulo para ejecutar: ")

            if opcion == "1":
                print("\n--- Lanzando Módulo de Clustering ---")
                try:
                    # Instanciar y ejecutar el menú de clustering
                    analizador_cluster = AnalisisDatos()
                    analizador_cluster.menu()
                except Exception as e:
                    print(f"ERROR al ejecutar el módulo de Clustering: {e}")
                print("--- Módulo de Clustering Finalizado ---")

            elif opcion == "2":
                print("\n--- Lanzando Módulo de Regresión con Red Neuronal ---")
                try:
                    # Instanciar y ejecutar el menú de regresión NN
                    analizador_nn = AnalisisRegresionNN()
                    analizador_nn.menu()
                except Exception as e:
                    print(f"ERROR al ejecutar el módulo de Regresión NN: {e}")
                print("--- Módulo de Regresión NN Finalizado ---")

            elif opcion == "0":
                print("Saliendo del menú de Machine Learning.")
                break

            else:
                print("Opción no válida. Por favor, intente de nuevo.")

# --- Código para Ejecutar el Módulo ---
if __name__ == "__main__":
    # Crear una instancia del menú principal de ML y mostrarlo
    menu_principal = MenuML()
    menu_principal.mostrar_menu()
