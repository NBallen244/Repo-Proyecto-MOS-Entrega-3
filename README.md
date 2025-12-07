#Estructura de Solucion/Repo Proyecto Etapa 3

El siguiente documento detalla la composición de la solución del proyecto etapa 3 mediante algoritmos genéticos, así como su combinación y comparación con soluciones previamente desarrolladas con modelos matemáticos implementados en la librería y solvers de Pyomo.

* Estructura de Solucion Global:
```bash
├───carga_datos (al igual que en la entrega anterior, conerva los archivos fuentes de cada caso, así como funciones para recurerarlos)
│   ├───project_a
│   │   ├───Proyecto_A_Caso2
│   │   └───Proyecto_A_Caso3
│   ├───Proyecto_Caso_Base
│   └───__pycache__
├───herramientas_compartidas
│   ├───matrices_distancia_tiempo
│   └───__pycache__
├───metaheuristica
│   ├───caso_2
│   ├───caso_3
│   ├───caso_base
│   └───__pycache__
└───pyomo
    ├───caso_2
    ├───caso_3
    └───caso_base
```