import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import ModelCheckpoint
import os
import time
import sys

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AnalisisRegresionNN:
    """
    Clase para manejar la carga de datos, aplicar Regresión con Red Neuronal (TensorFlow/Keras)
    y visualizar el ajuste, permitiendo la configuración de hiperparámetros.
    """
    def __init__(self, modelo_filepath="best_nn_model.keras"):
        """Inicializa la clase con rutas y variables de estado."""
        self.modelo_filepath = modelo_filepath
        self.df = None
        self.columnas_disponibles = []
        self.X, self.y = None, None
        self.X_train, self.X_val, self.y_train, self.y_val = (None,)*4
        self.feature_name, self.target_name = None, None
        self.model = None
        self.history = None
        # Los escaladores son cruciales para desescalar al graficar
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler() 
        self.hiperparametros = {} # Almacena los hiperparámetros del último entrenamiento

    def set_datos(self, dataframe):
        """
        Establece el dataframe de datos desde una fuente externa.
        """
        if dataframe is not None and not dataframe.empty:
            self.df = dataframe
            self.columnas_disponibles = self.df.select_dtypes(include=np.number).columns.tolist()
            if len(self.columnas_disponibles) < 2:
                print("ADVERTENCIA: Los datos cargados tienen menos de dos columnas numéricas.")
                self.df = None # Invalidar datos
            else:
                print("\nDatos externos cargados en el módulo de Regresión NN.")
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

    def seleccionar_y_preparar_datos(self):
        """Permite al usuario seleccionar X e Y, escala los datos y divide en train/val."""
        if self.df is None or len(self.columnas_disponibles) < 2:
            print("ERROR: Datos no cargados o insuficientes columnas numéricas.")
            return False

        print("\nColumnas numéricas disponibles:")
        for i, col in enumerate(self.columnas_disponibles):
            print(f"  {i+1}. {col}")

        try:
            # Columna X (Característica de Entrada)
            idx_x = int(input("Ingrese el número de la columna para X: ")) - 1
            if not (0 <= idx_x < len(self.columnas_disponibles)): raise IndexError
            self.feature_name = self.columnas_disponibles[idx_x]

            # Columna Y (Variable Objetivo)
            idx_y = int(input("Ingrese el número de la columna para Y (Objetivo): ")) - 1
            if not (0 <= idx_y < len(self.columnas_disponibles) or idx_x == idx_y): raise IndexError
            if idx_x == idx_y: raise ValueError("X e Y deben ser columnas diferentes.")
            self.target_name = self.columnas_disponibles[idx_y]

            # Preparación y Escalado
            X_raw = self.df[[self.feature_name]].values 
            y_raw = self.df[[self.target_name]].values 
            
            self.X = self.scaler_X.fit_transform(X_raw)
            self.y = self.scaler_y.fit_transform(y_raw)
            
            # División de Datos
            self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(
                self.X, self.y, test_size=0.2, random_state=42
            )
            print(f"\nDatos preparados. X: {self.feature_name}, Y: {self.target_name}.")
            print(f"Tamaños: Entrenamiento ({len(self.X_train)}), Validación ({len(self.X_val)})")
            return True

        except (ValueError, IndexError) as e:
            print(f"ERROR en la selección o datos: {e}. Vuelva a intentar.")
            return False
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False

    def configurar_hiperparametros(self):
        """Pide al usuario los hiperparámetros para el entrenamiento."""
        try:
            print("\n--- Configuración de Hiperparámetros ---")
            
            # Neuronas en Capas Ocultas (3 capas requeridas)
            n1 = int(input("Neuronas Capa Oculta 1 (e.g., 32): "))
            n2 = int(input("Neuronas Capa Oculta 2 (e.g., 16): "))
            n3 = int(input("Neuronas Capa Oculta 3 (e.g., 8): "))
            
            # Hiperparámetros de Entrenamiento
            epochs = int(input("Épocas de entrenamiento (e.g., 100): "))
            batch_size = int(input("Tamaño del lote (Batch Size) (e.g., 16): "))
            learning_rate = float(input("Tasa de Aprendizaje (Learning Rate, e.g., 0.001): "))

            if any(n <= 0 for n in [n1, n2, n3, epochs, batch_size]) or learning_rate <= 0:
                 raise ValueError("Todos los valores deben ser positivos.")

            self.hiperparametros = {
                'neuronas_c1': n1,
                'neuronas_c2': n2,
                'neuronas_c3': n3,
                'epochs': epochs,
                'batch_size': batch_size,
                'learning_rate': learning_rate,
                'optimizador': 'RMSprop',
                'loss': 'MSE',
                'activation': 'LeakyReLU'
            }
            return True
        except ValueError as e:
            print(f"ERROR: Entrada no válida. Asegúrese de ingresar números correctos. ({e})")
            return False

    def entrenar_red_neuronal(self):
        """Define, compila y entrena la red neuronal con los hiperparámetros dados."""
        if self.X_train is None or not self.hiperparametros:
            print("ERROR: Primero seleccione datos y configure hiperparámetros.")
            return

        params = self.hiperparametros
        start_time = time.time()
        
        # 3. Definición del Modelo Keras (Regresión)
        self.model = keras.Sequential([
            layers.Input(shape=(self.X_train.shape[1],)),  # Capa de entrada: 1 neurona (X)
            layers.Dense(params['neuronas_c1'], activation=keras.activations.leaky_relu, name='hidden_layer_1'),
            layers.Dense(params['neuronas_c2'], activation=keras.activations.leaky_relu, name='hidden_layer_2'),
            layers.Dense(params['neuronas_c3'], activation=keras.activations.leaky_relu, name='hidden_layer_3'),
            layers.Dense(1, activation=keras.activations.linear, name='output_layer_prediction') # Salida: 1 neurona (Y)
        ])

        # 4. Compilación del Modelo
        optimizer = keras.optimizers.RMSprop(learning_rate=params['learning_rate'])
        self.model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
        print("\n--- Resumen del Modelo ---")
        self.model.summary()

        # 5. Callback ModelCheckpoint
        checkpoint = ModelCheckpoint(
            self.modelo_filepath, monitor='val_mae', verbose=0, save_best_only=True, mode='min'
        )
        callbacks_list = [checkpoint]

        # 6. Entrenamiento del Modelo
        print("\nIniciando el entrenamiento de la red neuronal...")
        self.history = self.model.fit(
            self.X_train, self.y_train,
            epochs=params['epochs'], 
            batch_size=params['batch_size'],
            validation_data=(self.X_val, self.y_val),
            callbacks=callbacks_list,
            verbose=1 # Muestra progreso
        )

        end_time = time.time()
        print(f"\nEntrenamiento completado en {end_time - start_time:.2f} segundos.")
        print(f"El mejor modelo ha sido guardado en '{self.modelo_filepath}'")
        return True

    def graficar_y_registrar_resultados(self):
        """Carga el mejor modelo, genera gráficos de predicción/error/curvas y guarda registro."""
        if self.history is None:
            print("ERROR: Debe entrenar la red neuronal primero.")
            return

        try:
            best_trained_model = keras.models.load_model(self.modelo_filepath)
            print(f"\nModelo '{self.modelo_filepath}' cargado exitosamente para graficar.")
        except Exception as e:
            print(f"\nError al cargar el mejor modelo: {e}")
            print("Asegúrese de que el entrenamiento haya finalizado correctamente.")
            return

        # 1. Realizar Predicciones y Desescalar
        # Predicción sobre el conjunto de validación (escalado)
        y_pred_val_scaled = best_trained_model.predict(self.X_val)
        
        # Desescalar (Volver a la escala original)
        X_val_descaled = self.scaler_X.inverse_transform(self.X_val)
        y_val_descaled = self.scaler_y.inverse_transform(self.y_val)
        y_pred_val_descaled = self.scaler_y.inverse_transform(y_pred_val_scaled)
        
        # Opcional: Desescalar X_train para contexto
        X_train_descaled = self.scaler_X.inverse_transform(self.X_train)
        y_train_descaled = self.scaler_y.inverse_transform(self.y_train)

        # 2. Calcular Métricas de Error
        val_loss = self.history.history['val_loss'][-1]
        val_mae = self.history.history['val_mae'][-1]
        
        # 3. Guardar el Registro de Hiperparámetros
        registro_filename = "registro_hiperparametros.txt"
        with open(registro_filename, 'w') as f:
            f.write("--- Hiperparámetros de la Red Neuronal ---\n")
            for k, v in self.hiperparametros.items():
                f.write(f"{k}: {v}\n")
            f.write("\n--- Métricas de Validación Finales ---\n")
            f.write(f"Mean Squared Error (MSE): {val_loss:.4f}\n")
            f.write(f"Mean Absolute Error (MAE): {val_mae:.4f}\n")
        print(f"\nRegistro de hiperparámetros guardado en '{registro_filename}'")
        
        # 4. Generación de Gráficos
        
        # Gráfico A: Predicción vs. Datos Reales
        plt.figure(figsize=(10, 6))
        plt.scatter(X_train_descaled, y_train_descaled, label='Datos de Entrenamiento', alpha=0.5, s=15)
        plt.scatter(X_val_descaled, y_val_descaled, label='Datos de Validación (Reales)', alpha=0.8, s=30, color='orange')
        
        # Ordenar para una curva de predicción limpia (crucial si X no estaba ordenado)
        sort_indices = np.argsort(X_val_descaled[:, 0])
        plt.plot(X_val_descaled[sort_indices], y_pred_val_descaled[sort_indices], 
                 color='red', linewidth=3, label='Predicciones del Modelo')

        plt.title(f'Ajuste del Modelo NN: {self.target_name} vs {self.feature_name}')
        plt.xlabel(self.feature_name)
        plt.ylabel(self.target_name)
        plt.legend()
        plt.grid(True)
        plt.savefig("grafico_prediccion.png")
        plt.show()

        # Gráfico B: Curva de Pérdida (Loss)
        plt.figure(figsize=(10, 6))
        plt.plot(self.history.history['loss'], label='Pérdida Entrenamiento (MSE)')
        plt.plot(self.history.history['val_loss'], label='Pérdida Validación (MSE)')
        plt.title('Curva de Pérdida (Loss) durante el Entrenamiento')
        plt.xlabel('Época')
        plt.ylabel('Pérdida (MSE)')
        plt.legend()
        plt.grid(True)
        plt.savefig("grafico_curva_loss.png")
        plt.show()

        # Gráfico C: Curva de Error Absoluto (MAE)
        plt.figure(figsize=(10, 6))
        plt.plot(self.history.history['mae'], label='MAE Entrenamiento')
        plt.plot(self.history.history['val_mae'], label='MAE Validación')
        plt.title('Curva de Error Absoluto Medio (MAE) durante el Entrenamiento')
        plt.xlabel('Época')
        plt.ylabel('MAE')
        plt.legend()
        plt.grid(True)
        plt.savefig("grafico_curva_mae.png")
        plt.show()
        
        print("\nGráficos generados y guardados como 'grafico_prediccion.png', 'grafico_curva_loss.png', 'grafico_curva_mae.png'.")

    def menu(self):
        """Menú principal para interactuar con las funciones de la red neuronal."""
        if not self.cargar_datos():
            return

        while True:
            print("\n--- Menú Análisis de Regresión con Red Neuronal ---")
            print("1. Seleccionar columnas (X e Y) y Preparar Datos")
            print("2. Configurar Hiperparámetros (Neuronas, Lote, Épocas, Tasa)")
            print("3. Entrenar Red Neuronal")
            print("4. Generar Gráficos y Registro de Resultados")
            print("0. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                self.seleccionar_y_preparar_datos()
            elif opcion == "2":
                self.configurar_hiperparametros()
            elif opcion == "3":
                self.entrenar_red_neuronal()
            elif opcion == "4":
                self.graficar_y_registrar_resultados()
            elif opcion == "0":
                print("Saliendo del módulo de regresión NN.")
                break
            else:
                print("Opción no válida.")

# --- Código para Ejecutar el Módulo ---
if __name__ == "__main__":
    analizador_nn = AnalisisRegresionNN()
    analizador_nn.menu()
