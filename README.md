# Estructura de Solucion/Repo Proyecto Etapa 3

El siguiente documento detalla la composición de la solución del proyecto etapa 3 mediante algoritmos genéticos, así como su combinación y comparación con soluciones previamente desarrolladas con modelos matemáticos implementados en la librería y solvers de Pyomo. A continuacion resumimos la estructura del repositorio, la funcion de cada sección para el desarrollo de la solución, y cómo hace uso de las mismas (para las soluciones metaheuristicas):

* Estructura de Solucion Global:
```bash
├───carga_datos
│   ├───project_a
│   │   ├───Proyecto_A_Caso2
│   │       └───(archivos_fuentes_caso2)
│   │   └───Proyecto_A_Caso3
│   │       └───(archivos_fuentes_caso3)
│   ├───Proyecto_Caso_Base
│   │   └───(archivos_fuentes_base)
│   └───carga_datos.py (script que define la lectura de archivos para la carga de datos de cada caso)
├───herramientas_compartidas
│   ├───matrices_distancia_tiempo (resguarda las matrices o csv que indican el tiempo y distancia entre cada nodo de cada caso)
│   │       └───matriz_base.csv
│   │       └───matriz_2.csv
│   │       └───matriz_3.csv
│   ├───distancia.py (script con funciones de calculo de distancia para la generacion de la matrices)
│   └───visuales_resultados.py (script interactivo que permite generar visuales a partir de los archivos de verificacion de cada caso/metodo)
├───metaheuristica (resguarda las verificaciones y soluciones alternativas mediante algoritmos genéticos, así como la lógica replicable para cada caso)
│   ├───caso_2
│   ├───caso_3
│   ├───caso_base
│   └───funciones_ga.py
└───pyomo (estructura interna identica a la etapa 2, con la diferencia de referirse a las matrices distancia/tiempo de herramientas compartidas)
    ├───caso_2
    ├───caso_3
    └───caso_base
```

* Estructura Interna Por caso Metaheuristico (Ejemplo Caso Base):
```bash
├───metaheuristica
    ├───caso_2
    ├───caso_3
    ├───caso_base
    │   ├───main.py (script interactivo para la ejución de la solucion GA con los operadores compartidos con los parámetros ingresados. Adicionalmente genera el archivo de verificacion y despliega la convergencia del fitness (mean/max))
    │   ├───verificacion_metaheuristica_GA_caso_base.csv (archivo de verificación del caso)
    │   └───mapa_rutas.html (mapeo de rutas generado a partir de la herramienta compartidad de visuales con folium)
    └───funciones_ga.py (script de funciones/operadores GA generalizables a cada caso bajo nuestro contexto de proyecto)
```