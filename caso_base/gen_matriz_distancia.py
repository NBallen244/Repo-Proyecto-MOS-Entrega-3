import os
import sys
import pandas as pd

# Add the directory containing cargaBase.py to Python's search path
script_dir = os.path.dirname(os.path.abspath("cargaDatos.py"))
sys.path.insert(0, script_dir)

from herramientas_compartidas.distancia import gen_csv_distancia_tiempo
from carga_datos.cargaDatos import cargar_datos_base

if __name__ == "__main__":
    ruta_archivo="caso_base/matriz.csv"
    clientes, depositos = cargar_datos_base()[0:2]
    gen_csv_distancia_tiempo(ruta_archivo, clientes, depositos)