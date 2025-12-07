#Estructura de Solucion/Repo Proyecto Etapa 3

El siguiente documento detalla la composición de la solución del proyecto etapa 3 mediante algoritmos genéticos, así como su combinación y comparación con soluciones previamente desarrolladas con modelos matemáticos implementados en la librería y solvers de Pyomo. A continuacion resumimos la estructura del repositorio, y la funcion de cada sección para el desarrollo de la solución:

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
│   └───visuales_resultados.py (script interactivo que permite generar visuales a partir de los archivos de verificacion de cada caso/metodo, como distribucion de cargas entre vehiculos, mapa de rutas, y solucion alcanzada.)
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

* Estructura Interna Por caso Heuristico (Ejemplo Caso Base):
```bash
├───metaheuristica
    ├───caso_2
    ├───caso_3
    ├───caso_base
    │   ├───main.py (script interactivo principal que resguarda el algoritmo de solución mediante GA y la generación del archivo de verificación. Define su propio fitness y avance generacional por elitismo, reciclando las funciones GA compartidas. Se definen parametros por defecto (generaciones, probabilidad de mutacion, tamaño poblacion, etc), pero tambien la opción de parámetros personalizados para calibración). Adicionalmente despliega la convergencia resultante del fitness, tanto promedio como el mejor por cada generación.
    │   ├───verificacion_metaheuristica_GA_caso_base.csv
    │   └───mapa_rutas.html (generado a partir de la herramienta compartidad de visuales)
    └───funciones_ga.py (este script resguarda todas las funciones/operadores generalizables a todos los algoritmos geneticos de cada caso (mutacion, cruce, poblamiento inicial, reparacion, etc.) dado el contexto del proyecto. Lo único no incluido viene siendo la función de fitness (funcion objetivo) y el avance generacional por elitismo, definido en cada caso en función de su propio fitness)
