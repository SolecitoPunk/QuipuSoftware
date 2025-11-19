from Calculations.calculos import Calculos
import pandas as pd

class MenuCalculos:
    """
    Clase para mostrar un menú interactivo y ejecutar cálculos astronómicos.
    """
    def __init__(self):
        self.calculador = Calculos()
        self.datos = None

    def mostrar_menu(self, dataframe):
        """
        Muestra el menú principal de cálculos y maneja la selección del usuario.
        """
        if dataframe is None or dataframe.empty:
            print("ERROR: No se han cargado datos para realizar cálculos.")
            return

        self.datos = dataframe

        while True:
            print("\n--- Menú de Cálculos Astronómicos ---")
            print("1. Calcular Constante de Hubble (desde columnas)")
            print("2. Calcular Redshift (desde columnas)")
            print("3. Calcular Distancia por Ley de Hubble (desde columna redshift)")
            print("0. Volver al menú principal")

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                self._calcular_hubble_desde_columnas()
            elif opcion == "2":
                self._calcular_redshift_desde_columnas()
            elif opcion == "3":
                self._calcular_distancia_hubble_desde_columnas()
            elif opcion == "0":
                print("Volviendo al menú principal.")
                break
            else:
                print("Opción no válida. Por favor, intente de nuevo.")

    def _seleccionar_columnas(self, mensaje, num_columnas=1):
        """
        Función auxiliar para que el usuario seleccione una o más columnas del dataframe.
        """
        print("\nColumnas disponibles:")
        for i, col in enumerate(self.datos.columns):
            print(f"  {i+1}. {col}")

        seleccion = []
        for i in range(num_columnas):
            while True:
                try:
                    idx = int(input(f"{mensaje} ({i+1}/{num_columnas}): ")) - 1
                    if 0 <= idx < len(self.datos.columns):
                        seleccion.append(self.datos.columns[idx])
                        break
                    else:
                        print("Selección fuera de rango.")
                except ValueError:
                    print("Entrada no válida. Debe ser un número.")
        return seleccion if num_columnas > 1 else seleccion[0]

    def _calcular_hubble_desde_columnas(self):
        """
        Calcula la constante de Hubble utilizando columnas de velocidad y distancia.
        """
        print("\n--- Calcular Constante de Hubble ---")
        try:
            col_velocidad, col_distancia = self._seleccionar_columnas(
                "Seleccione la columna de velocidad (km/s) y luego la de distancia (Mpc)", 2
            )

            # Asegurarse de que las columnas son numéricas
            if pd.api.types.is_numeric_dtype(self.datos[col_velocidad]) and \
               pd.api.types.is_numeric_dtype(self.datos[col_distancia]):

                # Calcular H0 para cada fila y añadirla como una nueva columna
                self.datos['H0_calculado'] = self.datos.apply(
                    lambda row: self.calculador.calcularHubble(row[col_velocidad], row[col_distancia]),
                    axis=1
                )
                print("\nCálculo completado. Nueva columna 'H0_calculado' añadida.")
                print(self.datos[['H0_calculado']].describe())
            else:
                print("ERROR: Las columnas seleccionadas deben ser de tipo numérico.")

        except Exception as e:
            print(f"ERROR durante el cálculo: {e}")

    def _calcular_redshift_desde_columnas(self):
        """
        Calcula el redshift utilizando columnas de longitud de onda observada y emitida.
        """
        print("\n--- Calcular Redshift (z) ---")
        try:
            col_obs, col_emit = self._seleccionar_columnas(
                "Seleccione la columna de longitud observada y luego la de longitud emitida", 2
            )

            if pd.api.types.is_numeric_dtype(self.datos[col_obs]) and \
               pd.api.types.is_numeric_dtype(self.datos[col_emit]):

                self.datos['redshift_calculado'] = self.datos.apply(
                    lambda row: self.calculador.calcularRedshift(row[col_obs], row[col_emit]),
                    axis=1
                )
                print("\nCálculo completado. Nueva columna 'redshift_calculado' añadida.")
                print(self.datos[['redshift_calculado']].describe())
            else:
                print("ERROR: Las columnas seleccionadas deben ser de tipo numérico.")

        except Exception as e:
            print(f"ERROR durante el cálculo: {e}")

    def _calcular_distancia_hubble_desde_columnas(self):
        """
        Calcula la distancia de Hubble a partir de una columna de redshift.
        """
        print("\n--- Calcular Distancia por Ley de Hubble ---")
        try:
            col_redshift = self._seleccionar_columnas(
                "Seleccione la columna de redshift (z)", 1
            )

            if pd.api.types.is_numeric_dtype(self.datos[col_redshift]):
                self.datos['distancia_Mpc_calculada'] = self.datos[col_redshift].apply(
                    self.calculador.calcularDistanciaHubble
                )
                print("\nCálculo completado. Nueva columna 'distancia_Mpc_calculada' añadida.")
                print(self.datos[['distancia_Mpc_calculada']].describe())
            else:
                print("ERROR: La columna seleccionada debe ser de tipo numérico.")

        except Exception as e:
            print(f"ERROR durante el cálculo: {e}")

if __name__ == "__main__":
    # Ejemplo de uso (requiere un dataframe de prueba)
    data_ejemplo = {
        'velocidad': [680, 750, 700],
        'distancia': [10, 11, 9.8],
        'lambda_obs': [656.3, 660.0, 658.1],
        'lambda_emit': [650.0, 652.0, 651.5]
    }
    df_ejemplo = pd.DataFrame(data_ejemplo)

    menu_calc = MenuCalculos()
    menu_calc.mostrar_menu(df_ejemplo)
