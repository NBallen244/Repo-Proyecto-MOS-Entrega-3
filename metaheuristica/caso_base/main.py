import sys
import os
import time
import pandas as pd
from copy import deepcopy
import numpy as np

# Add the directory containing cargaBase.py to Python's search path
script_dir = os.path.dirname(os.path.abspath("cargaDatos.py"))
sys.path.insert(0, script_dir)

from carga_datos.cargaDatos import cargar_datos_base as cargar_datos
from metaheuristica import funciones_ga as ga

def calculo_fitness(cromosoma, matriz_distancias_tiempo:pd.DataFrame, deposito_idx:int, parametros:pd.DataFrame) -> float:
    """
    Calcula el fitness o costo total de las rutas representadas por un cromosoma en el contexto del problema MTSP.
    
    Returns:
        fitness (float): Costo total asociado a las rutas de la solución representada por el cromosoma.
    """
    costo=0.0
    precio_gasolina = parametros.loc[parametros['Parameter'] == 'fuel_price', 'Value'].values[0]
    rendimiento_gasolina = parametros.loc[parametros['Parameter'] == 'fuel_efficiency_typical', 'Value'].values[0]
    costo_km = precio_gasolina / rendimiento_gasolina  # Costo por km recorrido
    
    for index, ruta in enumerate(cromosoma):
        if len(ruta) == 0:
            continue
        distancia=ga.distancia_total_ruta(ruta, matriz_distancias_tiempo, deposito_idx)
        costo += distancia * costo_km
    return costo
        
        

def pasar_poblacion(poblacion, matriz_distancias_tiempo:pd.DataFrame, deposito_idx:int, parametros:pd.DataFrame, porcentaje_elitismo:float, probabilidad_mutacion:float, probabilidad_cruce:float, clientes:pd.DataFrame, vehiculos:pd.DataFrame):
    """
    Evolve the population to the next generation using elitism, crossover, and mutation.
    """
    # Evaluate current population
    population_fitness = [calculo_fitness(individual, matriz_distancias_tiempo, deposito_idx, parametros) for individual in poblacion]
    index_fitnesses = list(enumerate(population_fitness))
    
    # Organizar por fitness (menor es mejor)
    index_fitnesses.sort(key=lambda x: x[1])
    
    # Conservar los mejores individuos (elitismo)
    num_elite = max(1, int(porcentaje_elitismo * len(poblacion)))
    elite_indices = [idx for idx, _ in index_fitnesses[:num_elite]]
    new_population = [deepcopy(poblacion[idx]) for idx in elite_indices]
    
    # Llenamos con hijos
    while len(new_population) < len(poblacion):
        #Escoger padres
        parent1, parent2 = ga.seleccion_ruleta(poblacion, population_fitness)
        #Obtener hijos por cruce
        hijo1, hijo2 = ga.crossover(parent1, parent2, probabilidad_cruce)
        #Mutar hijos
        hijo1 = ga.mutate(hijo1, probabilidad_mutacion)
        hijo2 = ga.mutate(hijo2, probabilidad_mutacion)
        #reparamos hijos en caso de inconsistencias
        hijo1=ga.reparar_solucion(hijo1, clientes, matriz_distancias_tiempo, deposito_idx, vehiculos)
        hijo2=ga.reparar_solucion(hijo2, clientes, matriz_distancias_tiempo, deposito_idx, vehiculos)
        # Agregar hijos a la nueva población
        new_population.append(hijo1)
        new_population.append(hijo2)
    
    return new_population[:len(poblacion)]  # Asegurar tamaño constante de la población

def solve(verbose=True, generaciones=100, tam_poblacion=100, porcentaje_elitismo=0.1, probabilidad_mutacion=0.1, probabilidad_cruce=0.7, max_sin_mejora=50):
    """
    Ejecuta el algoritmo genético para optimizar las rutas de vehículos en el problema CVRP.
    
    Args:
        verbose (bool): Imprimir progreso si es True
        generaciones (int): Número máximo de generaciones
        tam_poblacion (int): Tamaño de la población
        porcentaje_elitismo (float): Porcentaje de elitismo
        probabilidad_mutacion (float): Probabilidad de mutación
        probabilidad_cruce (float): Probabilidad de cruce
        
    Returns:
        mejor_solucion (list): La mejor solución encontrada,
        mejor_fitness (float): El fitness de la mejor solución,
        historial_fitness_promedio (list): Historial de fitness promedio a lo largo de las generaciones
        historial_mejor_fitness (list): Historial del mejor fitness a lo largo de las generaciones
    """
    #Recuperamos datos de entrada
    clientes, depositos, parametros, vehiculos = cargar_datos()
    matriz_distancia_tiempo = pd.read_csv("herramientas_compartidas/matrices_distancia_tiempo/matriz_base.csv")
    deposito_idx = depositos['StandardizedID'].iloc[0]
    clientes_ids = clientes['StandardizedID'].tolist()
    num_vehiculos = vehiculos.shape[0]
    #inicializamos historiales
    fitness_prom_history = []
    best_fitness_history = []
    # Initialize population
    poblacion=ga.inicializar_poblacion(tam_poblacion, clientes_ids, num_vehiculos)
    #reparmos la poblacion inicial
    for i in range(len(poblacion)):
        poblacion[i]=ga.reparar_solucion(poblacion[i], clientes, matriz_distancia_tiempo, deposito_idx, vehiculos)
    # Calculamos fitnesses iniciales para el historial
    fitnesses_iniciales = [calculo_fitness(individual, matriz_distancia_tiempo, deposito_idx, parametros) for individual in poblacion]
    fitness_prom_history.append(np.mean(fitnesses_iniciales))
    best_fitness_history.append(np.min(fitnesses_iniciales))
    
    # Track best solution and convergence
    best_solution = None
    best_fitness = float('inf')
    generations_without_improvement = 0
    start_time = time.time()
    
    # Main loop
    for generation in range(generaciones):
        # Pasamos de generacion
        poblacion = pasar_poblacion(poblacion, matriz_distancia_tiempo, deposito_idx, parametros, porcentaje_elitismo, probabilidad_mutacion, probabilidad_cruce, clientes, vehiculos)
        
        #Encontramos la mejor solucion de la generacion actual y sus fitnesses
        current_best = None
        current_best_fitness = float('inf')
        fitnesses=[]
        
        for solution in poblacion:
            fitness = calculo_fitness(solution, matriz_distancia_tiempo, deposito_idx, parametros)
            fitnesses.append(fitness)
            if fitness < current_best_fitness:
                current_best = solution
                current_best_fitness = fitness
        #Guardamos el fitness promedio y mejor fitness de la generacion actual
        fitness_prom_history.append(np.mean(fitnesses))
        best_fitness_history.append(current_best_fitness)
        # Cambiamos las solucion global si encontramos una mejor
        if current_best_fitness < best_fitness:
            best_solution = deepcopy(current_best)
            best_fitness = current_best_fitness
            generations_without_improvement = 0
        else:
            generations_without_improvement += 1
        
        # Print progress
        if verbose and generation % 10 == 0:
            elapsed_time = time.time() - start_time
            print(f"Generacion {generation}: Mejor Fitness = {best_fitness:.2f}, "
                    f"Mejor Actual = {current_best_fitness:.2f}, "
                    f"Tiempo = {elapsed_time:.2f}s")
        
        # Early stopping
        if generations_without_improvement >= max_sin_mejora:
            if verbose:
                print(f"Terminando en {generation} debido a no mejora "
                        f"por {max_sin_mejora} generaciones.")
            break
    
    if verbose:
        total_time = time.time() - start_time
        print(f"Optimización completa. Mejor fitness: {best_fitness:.2f}, "
                f"Tiempo: {total_time:.2f}s")
        
    return best_solution, best_fitness, fitness_prom_history, best_fitness_history

if __name__ == "__main__":
    tamaño_poblacion = 50
    num_generaciones = 100
    prob_mutacion = 0.1
    prob_cruce = 0.7
    porcentaje_elitismo = 0.1
    defecto=input("Iniciando optimización con algoritmo genético...Usar parámetros por defecto?(S/N): ")
    if defecto.lower()=='n':
        tamaño_poblacion=int(input("\nIngrese el tamaño de la población: "))
        num_generaciones=int(input("Ingrese el número de generaciones: "))
        prob_mutacion=float(input("Ingrese la probabilidad de mutación (0-1): "))
        prob_cruce=float(input("Ingrese la probabilidad de cruce (0-1): "))
        porcentaje_elitismo=float(input("Ingrese el porcentaje de elitismo (0-1): "))
        print("\nIniciando optimización con los parámetros personalizados...")
    mejor_solucion, mejor_fitness, historial_fitness_promedio, historial_mejor_fitness = solve(verbose=True, generaciones=num_generaciones, tam_poblacion=tamaño_poblacion, porcentaje_elitismo=porcentaje_elitismo, probabilidad_mutacion=prob_mutacion, probabilidad_cruce=prob_cruce, max_sin_mejora=num_generaciones//2)
    print("Mejor Solución Encontrada:")
    print(mejor_solucion)
    print(f"Con un fitness de: {mejor_fitness:.2f}")
    #diccionario resultados
    guardar=bool(input("¿Desea guardar los resultados en un archivo CSV para verificación? (S/N): ").lower()=='s')
    if guardar:
        resultados = {
            "VehicleId": [],
            "LoadCap": [],
            "FuelCap": [],
            "RouteSequence": [],
            "Municipalities": [],
            "DemandSatisfied": [],
            "InitialLoad": [],
            "InitialFuel": [],
            "Distance": [],
            "Time": [],
            "TotalCost": []
        }
        clientes, depositos, parametros, vehiculos = cargar_datos()
        matriz_distancia_tiempo = pd.read_csv("herramientas_compartidas/matrices_distancia_tiempo/matriz_base.csv")
        deposito_index = depositos['StandardizedID'].iloc[0]
        precio_gasolina = parametros.loc[parametros['Parameter'] == 'fuel_price', 'Value'].values[0]
        rendimiento_gasolina = parametros.loc[parametros['Parameter'] == 'fuel_efficiency_typical', 'Value'].values[0]
        costo_km = precio_gasolina / rendimiento_gasolina  # Costo por km recorrido
        
        #Contruccion archivo de verificacion de resultados
        for index, ruta in enumerate(mejor_solucion):
            vehicleid = vehiculos['StandardizedID'].iloc[index]
            municipios = len(ruta)
            #reconstruimos la ruta completa con deposito al inicio y final
            ruta_final = [deposito_index]  # Empezamos en el depósito
            for cliente in ruta:
                ruta_final.append(cliente)
            ruta_final.append(deposito_index)  # Volvemos al depósito
            demandas_satisfecha = []
            demanda_total=0
            distancia_recorrida=ga.distancia_total_ruta(ruta, matriz_distancia_tiempo, deposito_index)
            tiempo_total=ga.tiempo_total_ruta(ruta, matriz_distancia_tiempo, deposito_index)
            #obtenemos demandas satisfechas
            for cliente in ruta:
                demanda_cliente = clientes.loc[clientes['StandardizedID'] == cliente, 'Demand'].values[0]
                demandas_satisfecha.append(str(demanda_cliente))  # +1 para ajustar el índice de orden
                demanda_total += demanda_cliente
            if len(demandas_satisfecha) == 0:
                demandas_satisfecha.append('0')
        
            texto_ruta="-".join(ruta_final)
            resultados["VehicleId"].append(vehicleid)
            resultados["LoadCap"].append(vehiculos.loc[vehiculos['StandardizedID'] == vehicleid, 'Capacity'].values[0])
            resultados["FuelCap"].append(vehiculos.loc[vehiculos['StandardizedID'] == vehicleid, 'Range'].values[0]/(rendimiento_gasolina))  # Asumiendo tanque lleno
            resultados["RouteSequence"].append(texto_ruta)
            resultados["Municipalities"].append(municipios)
            resultados["DemandSatisfied"].append("-".join(demandas_satisfecha))
            resultados["InitialLoad"].append(demanda_total)  # Asumiendo carga inicial igual a demanda satisfecha
            resultados["InitialFuel"].append(distancia_recorrida / (rendimiento_gasolina))  # Asumiendo tanque lleno
            resultados["Distance"].append(distancia_recorrida)
            resultados["Time"].append(tiempo_total) 
            total_cost = distancia_recorrida * costo_km
            resultados["TotalCost"].append(total_cost)
            
        #guardar dataframe
        data_frame=pd.DataFrame(resultados)
        #export csv
        data_frame.to_csv('metaheuristica/caso_base/verificacion_metaheuristica_GA_caso_base.csv', sep=',', index=False)
    mostrar_historial = input("¿Quiere ver el historial de fitness promedio y mejor fitness a lo largo de las generaciones? (S/N): ")
    if mostrar_historial.lower() == 's':
        ga.plot_convergence(historial_fitness_promedio, historial_mejor_fitness)