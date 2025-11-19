import unittest
import csv
import os
from typing import List, Dict, Any
from entrada import Entrada  # importa tu clase (ajusta si está en otro archivo)


class TestEntrada(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada test."""
        # Creamos un archivo CSV temporal con datos de prueba
        self.nombre_archivo = "test_datos.csv"
        with open(self.nombre_archivo, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["nombre", "valor"])
            writer.writeheader()
            writer.writerow({"nombre": "Galaxia A", "valor": "123"})
            writer.writerow({"nombre": "Galaxia B", "valor": "456"})

        self.entrada = Entrada(self.nombre_archivo)

    def tearDown(self):
        """Se ejecuta después de cada test."""
        if os.path.exists(self.nombre_archivo):
            os.remove(self.nombre_archivo)

    def test_leerDatos_correcto(self):
        """Prueba que se lean correctamente los datos del CSV."""
        datos = self.entrada.leerDatos()
        self.assertEqual(len(datos), 2)
        self.assertEqual(datos[0]["nombre"], "Galaxia A")

    def test_leerDatos_archivo_no_existente(self):
        """Prueba el manejo de archivo no encontrado."""
        entrada_invalida = Entrada("no_existe.csv")
        datos = entrada_invalida.leerDatos()
        self.assertEqual(datos, [])  # Debe retornar lista vacía


if __name__ == "__main__":
    unittest.main()

