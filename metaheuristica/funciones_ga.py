
from copy import deepcopy 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
def inicializar_poblacion(numero_individuos:int, clientes_ids:list, num_vehiculos:int):
    """
    Crear una población inicial de soluciones aleatorias.
    
    Cada solución se representa como una lista de rutas, una para cada viajero.
    Cada ruta es una secuencia de clientes (excluyendo el depósito, que es implícito al inicio y al final).
    """
    population = []
    
    for i in range(numero_individuos):
        # Create a random solution
        solution = solucionAleatoria(clientes_ids, num_vehiculos)
        population.append(solution)
    
    return population

def solucionAleatoria(clientes_ids:list, num_vehiculos:int):
    """
    Crear una solución aleatoria válida.
    
    Returns:
        Cromosoma, o lista de rutas (una por vehiculo).
    """
    # Tomamos los clientes a visitar y los mezclamos aleatoriamente
    clientes_a_visitar = clientes_ids.copy()
    random.shuffle(clientes_a_visitar)
    
    # Partition the cities among travelers
    num_vehiculos=num_vehiculos
    routes = [[] for _ in range(num_vehiculos)]
    
    # Dsitribuimos equitativamente o aleatoriamente
    if random.random() < 0.5:  # Distribute evenly
        clientes_por_vehiculo = len(clientes_a_visitar) // num_vehiculos
        remainder = len(clientes_a_visitar) % num_vehiculos
        
        start_idx = 0
        for i in range(num_vehiculos):
            # Add one extra city to some travelers if there's a remainder
            extra = 1 if i < remainder else 0
            end_idx = start_idx + clientes_por_vehiculo + extra
            routes[i] = clientes_a_visitar[start_idx:end_idx]
            start_idx = end_idx
    else:  # Distribuimos al azar (aceptando rutas vacias) hasta entregar todos los clientes
        while clientes_a_visitar:
            traveler_idx = random.randint(0, num_vehiculos - 1)
            routes[traveler_idx].append(clientes_a_visitar.pop(0))
            
    return routes


def seleccion_ruleta(poblacion:list, fitness_poblacion:list):
    """
    Seleleccionamos padres por método de ruleta.
    
    Returns:
        Tupla con los dos padres seleccionados
    """
    fitness_total = sum(fitness_poblacion)
    selection_probs = [1 - (f / fitness_total) for f in fitness_poblacion]
    padre1 = random.choices(poblacion, weights=selection_probs, k=1)[0]
    padre2 = random.choices(poblacion, weights=selection_probs, k=1)[0]
    while padre2 == padre1:
        padre2 = random.choices(poblacion, weights=selection_probs, k=1)[0]
  
    return padre1, padre2

def crossover(padre1:list, padre2:list, probabilidad_cruce:float=0.7):
    """
    Hace el cruce sobre los padres.
    
    Siendo MTSP equivalente a CVRP, se usan dos tipos de cruces:
    1. Intercambio de Rutas - intercambia rutas completas entre padres
    2. Fusión de Rutas - fusiona rutas entre padres y redistribuye ciudades
    
    Returns:
        Dos hijos resultantes del cruce
    """
    if random.random() > probabilidad_cruce:
        return deepcopy(padre1), deepcopy(padre2)
    
    # Choose crossover type: route exchange or route merge
    if random.random() < 0.5:
        return cruce_intercambio(padre1, padre2)
    else:
        return cruce_fusion(padre1, padre2)

def cruce_intercambio(padre1:list, padre2:list):
    """
    Intercambio de Rutas: intercambia rutas completas entre dos padres.
    
    Esto preserva buenas rutas mientras crea nuevas combinaciones.
    """
    child1 = deepcopy(padre1)
    child2 = deepcopy(padre2)
    
    if len(padre1) < 2:
        return child1, child2
        
    # Select random routes to exchange
    num_routes_to_exchange = random.randint(1, max(1, len(padre1) // 2))
    routes_to_exchange = random.sample(range(len(padre1)), num_routes_to_exchange)
    
    # Exchange the selected routes
    for route_idx in routes_to_exchange:
        child1[route_idx], child2[route_idx] = child2[route_idx], child1[route_idx]
        
    
    return child1, child2

def cruce_fusion(padre1:list, padre2:list):
    """
    Fusión de Rutas - fusiona rutas entre padres y redistribuye ciudades
    
    Esto combina partes de rutas de ambos padres, creando más diversidad genética.
    """
    num_rutas = len(padre1)

    # Reinicializar hijos vacíos
    child1 = [[] for _ in range(num_rutas)]
    child2 = [[] for _ in range(num_rutas)]
    
    # Para cada ruta, mezclar segmentos de ambos padres
    for i in range(num_rutas):
        # Escojer pivotes de cruce aleatorios para cada padre
        if padre1[i] and padre2[i]:
            p1_cross = random.randint(0, len(padre1[i]))
            p2_cross = random.randint(0, len(padre2[i]))
            
            # Combinar segmentos de ambos padres
            merged1 = padre1[i][:p1_cross] + padre2[i][p2_cross:]
            merged2 = padre2[i][:p2_cross] + padre1[i][p1_cross:]
            #agregar nuevas rutas a los hijos
            child1[i] = merged1
            child2[i] = merged2
    
    return child1, child2


def eliminar_duplicados_globales(cromosoma:list):
    """
    Elimina clientes duplicados en todas las rutas del cromosoma.
    Solo se conserva la primera aparición de cada cliente.
    """
    ciudades_visitadas = set()
        
    #eliminamos duplicados globales (sin clientes repetidos entre rutas, solo conservando la primera aparicion)
    for index, ruta in enumerate(cromosoma):
        nueva_ruta = []
        for ciudad in ruta:
            if ciudad not in ciudades_visitadas:
                ciudades_visitadas.add(ciudad)
                nueva_ruta.append(ciudad)
        cromosoma[index] = nueva_ruta
    
    return cromosoma , ciudades_visitadas

def distancia_total_ruta(ruta:list, matriz_distancias_tiempos:pd.DataFrame, deposito_id:str):
    """
    Calcula la distancia total de una ruta, incluyendo el viaje de ida y vuelta al depósito.
    """
    if not ruta:
        return 0
    
    total_distance = 0
    # Desde el depósito al primer cliente
    distancia_dept = matriz_distancias_tiempos.loc[
                (matriz_distancias_tiempos['FromID'] == deposito_id) & (matriz_distancias_tiempos['ToID'] == ruta[0]),
                'Distance_km'
            ].values[0]
    total_distance += distancia_dept
    
    nodo_actual = ruta[0]
    # Entre clientes en la ruta
    for siguiente_nodo in ruta[1:]:
        distancia_entre = matriz_distancias_tiempos.loc[
                (matriz_distancias_tiempos['FromID'] == nodo_actual) & (matriz_distancias_tiempos['ToID'] == siguiente_nodo),
                'Distance_km'
            ].values[0]
        total_distance += distancia_entre
        nodo_actual = siguiente_nodo
    
    # Desde el último cliente de vuelta al depósito
    distancia_dept_vuelta = matriz_distancias_tiempos.loc[
                (matriz_distancias_tiempos['ToID'] == ruta[-1]) & (matriz_distancias_tiempos['FromID'] == deposito_id),
                'Distance_km'
            ].values[0]
    total_distance += distancia_dept_vuelta
    
    return total_distance

def tiempo_total_ruta(ruta:list, matriz_distancias_tiempos:pd.DataFrame, deposito_id:str):
    """
    Calcula el tiempo total de una ruta, incluyendo el viaje de ida y vuelta al depósito.
    """
    if not ruta:
        return 0
    
    total_time = 0
    # Desde el depósito al primer cliente
    tiempo_dept = matriz_distancias_tiempos.loc[
                (matriz_distancias_tiempos['FromID'] == deposito_id) & (matriz_distancias_tiempos['ToID'] == ruta[0]),
                'Time_min'
            ].values[0]
    total_time += tiempo_dept
    
    nodo_actual = ruta[0]
    # Entre clientes en la ruta
    for siguiente_nodo in ruta[1:]:
        tiempo_entre = matriz_distancias_tiempos.loc[
                (matriz_distancias_tiempos['FromID'] == nodo_actual) & (matriz_distancias_tiempos['ToID'] == siguiente_nodo),
                'Time_min'
            ].values[0]
        total_time += tiempo_entre
        nodo_actual = siguiente_nodo
    
    # Desde el último cliente de vuelta al depósito
    tiempo_dept_vuelta = matriz_distancias_tiempos.loc[
                (matriz_distancias_tiempos['ToID'] == ruta[-1]) & (matriz_distancias_tiempos['FromID'] == deposito_id),
                'Time_min'
            ].values[0]
    total_time += tiempo_dept_vuelta
    
    return total_time

def demanda_total_ruta(ruta:list, clientes:pd.DataFrame):
    """
    Calcula la demanda total de una ruta sumando las demandas de todos los clientes en la ruta.
    """
    total_demand = 0
    for cliente_id in ruta:
        demanda_cliente = clientes.loc[clientes['StandardizedID'] == cliente_id, 'Demand'].values[0]
        total_demand += demanda_cliente
    return total_demand

def verificar_capacidad(ruta:list, clientes:pd.DataFrame, capacidad_vehiculo:int):
    """
    Verifica si la demanda total de una ruta excede la capacidad del vehículo.
    
    Returns:
        True si la ruta es factible (no excede capacidad), False si no lo es.
    """
    demanda_ruta = demanda_total_ruta(ruta, clientes)
    return demanda_ruta <= capacidad_vehiculo

def reparacion_por_capacidad(cromosoma, clientes:pd.DataFrame, vehiculos:pd.DataFrame):
    """
    Repara rutas que exceden la capacidad del vehículo.
    
    Si una ruta excede la capacidad, mueve clientes al final de la ruta a otras rutas con capacidad disponible.
    """
    for ruta_idx, ruta in enumerate(cromosoma):
        capacidad_vehiculo = vehiculos.loc[vehiculos.index == ruta_idx, 'Capacity'].values[0]
        
        while not verificar_capacidad(ruta, clientes, capacidad_vehiculo):
            # Mover el último cliente a otra ruta
            cliente_a_mover = ruta.pop()  # Remover el último cliente
            
            # Buscar una ruta alternativa con capacidad disponible
            for otra_ruta_idx, otra_ruta in enumerate(cromosoma):
                if otra_ruta_idx != ruta_idx:
                    capacidad_otra_vehiculo = vehiculos.loc[vehiculos.index == otra_ruta_idx, 'Capacity'].values[0]
                    if verificar_capacidad(otra_ruta + [cliente_a_mover], clientes, capacidad_otra_vehiculo):
                        otra_ruta.append(cliente_a_mover)
                        break
            else:
                # Si no se encontró una ruta alternativa, volver a agregar el cliente a la ruta original
                ruta.append(cliente_a_mover)
                break  # Salir del bucle para evitar un ciclo infinito
    return cromosoma

def optimizar_ruta2opt(ruta:list, matriz_distancias_tiempos:pd.DataFrame, deposito_id:str, iteraciones:int=5):
    """
    Optimiza una ruta usando el algoritmo de 2-opt para minimizar la distancia total.
    """
    if len(ruta) < 3:
        return ruta  # No hay suficiente ciudades para optimizar
    
    improved = True
    best_route = ruta
    best_distance = distancia_total_ruta(best_route, matriz_distancias_tiempos, deposito_id)
    repeticiones = 0
    while improved and repeticiones < iteraciones:
        improved = False
        for i in range(1, len(best_route) - 1):
            for j in range(i + 1, len(best_route)):
                if j - i == 1:  # No se puede invertir segmentos adyacentes
                    continue
                new_route = best_route[:i] + best_route[i:j][::-1] + best_route[j:]
                new_distance = distancia_total_ruta(new_route, matriz_distancias_tiempos, deposito_id)
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True
        ruta = best_route
    
    return best_route
def reparar_solucion(cromosoma:list, clientes:pd.DataFrame, matriz_distancias_tiempos:pd.DataFrame, deposito_id:str, vehiculos:pd.DataFrame):
    """
    Repara una solucion para ser factible deacuerdo a las restricciones del modelo.
    
    1. Elimina duplicados globales
    2. Enceuntra clientes faltantes y los agrega aleatoriamente a diferentes rutas
    3. Remove duplicates and add missing cities
    """
    # Eliminar duplicados globales (los clientes son atentidos una unica vez)
    cromosoma, ciudades_visitadas = eliminar_duplicados_globales(cromosoma)
    # Encontrar clientes faltantes (todos los clientes que no estan en ninguna ruta)
    clientes_ids = clientes['StandardizedID'].tolist()
    missing_cities = [cliente for cliente in clientes_ids if cliente not in ciudades_visitadas]
    # Agregar clientes faltantes a rutas aleatorias (todas las demandas deben ser cumplidas)
    random.shuffle(missing_cities)
    for client in missing_cities:
        # Escojemos ruta de menor tamaño (asumiendo que tiene mas capacidad)
        route_sizes = [(i, len(route)) for i, route in enumerate(cromosoma)]
        route_idx = min(route_sizes, key=lambda x: x[1])[0]
        # Insertamos en una posicion al azar
        insert_pos = random.randint(0, len(cromosoma[route_idx]))
        cromosoma[route_idx].insert(insert_pos, client)
    #Reparamos para cumplir la restriccion de capacidad
    cromosoma = reparacion_por_capacidad(cromosoma, clientes, vehiculos)
    #Optimizamos cada ruta con 2-opt
    for ruta_idx, ruta in enumerate(cromosoma):
        cromosoma[ruta_idx] = optimizar_ruta2opt(ruta, matriz_distancias_tiempos, deposito_id)
    return cromosoma

def mutate(cromosoma:list, probabilidad_mutacion:float=0.1):
    """
    Apply mutation operators to the solution.
    
    Uses several mutation types:
    1. Swap mutation - swaps cities within a route
    2. Insert mutation - moves a city to a different position
    3. Inversion mutation - reverses a segment of a route
    4. Redistribution mutation - moves cities between routes
    
    Returns:
        Mutated solution
    """
    if random.random() > probabilidad_mutacion:
        return cromosoma
        
    # Choose mutation type
    mutation_type = random.choice(['swap', 'insert', 'invert', 'redistribute'])
    
    if mutation_type == 'swap':
        return _swap_mutation(cromosoma)
    elif mutation_type == 'insert':
        return _insert_mutation(cromosoma)
    elif mutation_type == 'invert':
        return _inversion_mutation(cromosoma)
    else:  # redistribute
        return _redistribution_mutation(cromosoma)

def _swap_mutation(solution):
    """Reubica dos ciudades aleatoriamente dentro de una ruta aleatoria."""
    mutated = deepcopy(solution)
    
    # Escojer una ruta no vacía
    non_empty_routes = [i for i, route in enumerate(mutated) if len(route) >= 2]
    if not non_empty_routes:
        return mutated
        
    route_idx = random.choice(non_empty_routes)
    route = mutated[route_idx]
    
    # Intercambiar dos posiciones aleatorias
    pos1, pos2 = random.sample(range(len(route)), 2)
    route[pos1], route[pos2] = route[pos2], route[pos1]
    
    return mutated

def _insert_mutation(solution):
    """Mueve una ciudad aleatoria a una posición diferente en su ruta."""
    mutated = deepcopy(solution)
    
    # Escojer una ruta no vacía
    non_empty_routes = [i for i, route in enumerate(mutated) if len(route) >= 2]
    if not non_empty_routes:
        return mutated
        
    route_idx = random.choice(non_empty_routes)
    route = mutated[route_idx]
    
    # Seleccionar una ciudad y una nueva posición
    old_pos = random.randint(0, len(route) - 1)
    new_pos = random.randint(0, len(route) - 1)
    while new_pos == old_pos:
        new_pos = random.randint(0, len(route) - 1)
        
    # Remover la ciudad de la posición antigua e insertarla en la nueva posición
    city = route.pop(old_pos)
    route.insert(new_pos, city)
    
    return mutated

def _inversion_mutation(solution):
    """Invertir un segmento de una ruta aleatoria."""
    mutated = deepcopy(solution)
    
    # Escojer una ruta con suficientes ciudades para invertir
    eligible_routes = [i for i, route in enumerate(mutated) if len(route) >= 3]
    if not eligible_routes:
        return mutated
        
    route_idx = random.choice(eligible_routes)
    route = mutated[route_idx]
    
    # Select two positions and reverse the segment between them
    pos1, pos2 = sorted(random.sample(range(len(route)), 2))
    mutated[route_idx] = route[:pos1] + route[pos1:pos2+1][::-1] + route[pos2+1:]
    
    return mutated

def _redistribution_mutation(solution):
    """Mover una ciudad de una ruta a otra."""
    mutated = deepcopy(solution)
    number_of_routes = len(mutated)
    
    if number_of_routes < 2:
        return mutated
        
    # Escojer rutas no vacías
    non_empty_routes = [i for i, route in enumerate(mutated) if route]
    if not non_empty_routes:
        return mutated
     
    #Escoge dos rutas no vacias diferentes   
    from_route_idx = random.choice(non_empty_routes)
    to_route_idx = random.randint(0, number_of_routes - 1)
    while to_route_idx == from_route_idx:
        to_route_idx = random.randint(0, number_of_routes - 1)
        
    # Mover una ciudad de from_route a to_route
    if mutated[from_route_idx]:
        city_pos = random.randint(0, len(mutated[from_route_idx]) - 1)
        city = mutated[from_route_idx].pop(city_pos)
        
        insert_pos = random.randint(0, len(mutated[to_route_idx]))
        mutated[to_route_idx].insert(insert_pos, city)
        
    return mutated


def plot_convergence(historial_fitness:list, mejor_historial_soluciones:list):
    """Plot the convergence of the genetic algorithm."""
    plt.figure(figsize=(10, 6))
    plt.plot(historial_fitness, label='Fitness Promedio')
    plt.plot(mejor_historial_soluciones, label='Mejor Fitness Generación')
    plt.xlabel('Generation')
    plt.ylabel('Fitness (Total Cost)')
    plt.title('Genetic Algorithm Convergence')
    plt.legend()
    plt.grid(True)
    plt.show()