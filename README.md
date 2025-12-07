# Solucion/Repo Proyecto Etapa 3 para uso de Metaheuristica (Algoritmos Genéticos)

El siguiente documento detalla la composición de la solución del proyecto etapa 3 mediante algoritmos genéticos, así como su combinación y comparación con soluciones previamente desarrolladas con modelos matemáticos implementados en la librería y solvers de Pyomo. A continuacion resumimos la estructura del repositorio, la funcion de cada sección para el desarrollo de la solución, y cómo hace uso de las mismas (para las soluciones metaheuristicas):

## Estructura de Solucion Global:
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

## Estructura Interna Por caso Metaheuristico (Ejemplo Caso Base):
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
## Pasos para utilizar los scripts solucion de cada caso:
1. De faltar las matrices de distancia tiempo, ejecutar los generadores de matrices heredados de la implementacion de pyomo de la entrega anterior (ubicados en la carpeta de pyomo en cada caso)
2. Para cada caso (en la carpeta de metaheuristica), ejecutar el script main.py, el cual guíara en la definición de los parámetros.
3. En terminal escojer los parámetros (tamaño poblacion, numero de generaciones, probabilidades mut/cruce, y porcentaje de elitismo (0-1)), o los valores que definimos por defecto bajo estandares (50 de poblacion, 100 generaciones, 0.7 cruce, 0.1 de mutacion, y 0.1 de elitismo)
4. Confirmar y esperar a la ejecución (descrita cada 10 generaciones). Si se detecta que más de la mitad de las generaciones no ha aportado un mejor fitness, se termina la ejecución.
5. Se despliega el cromosoma de la solucion, el fitness final (costo) y el tiempo de ejecución total. 
6. Si se quiere sobreescribir el archivo de verificacion, confirmar (los archivos enviados fueron bajo parámetros por defecto de una ejecucion), guardando la copia actualizada en la carpeta del caso correspondiente.
7. Tras ello, decide si desplegar o no la evolución de los fitnesses promedio y top en cada generación, con lo cual se muestra un gráfico de matplotlib de dos lineas representando dichas evoluciones.
8. Si se quiere ver la rutas (asegurandonos de que sea sobre el último archivo de verificacion sobreescrito), ir a herramientas_compartidas/visuales_resultados.py, ejecutar y seleccionar el caso correspondiente, y luego la opción 1 (Generar Mapa Rutas). Esto desplegará el mapa folium, y lo guardará como .html en la carpeta del caso correspondiente.
9. Adicionalmente, en este mismo script se dará la opción para visualizar la solución calculada en el archivo de verificacion (suma de costo), así como la distribución de la carga entre los vehiculos (mostrandose en un gráfico de lineas y barras la capacidad del vehiculo, la carga que llevo, y como resultado el porcentaje de espacio no usado por este, o en un gráfico de torta). Seguir las instrucciones en terminal para revisar diferentes visuales y/o diferentes archivos de verificación.