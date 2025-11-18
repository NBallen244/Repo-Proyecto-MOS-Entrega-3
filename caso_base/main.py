from pyomo.environ import *
from pyomo.opt import SolverFactory

import sys
import os
import time

# Add the directory containing cargaBase.py to Python's search path
script_dir = os.path.dirname(os.path.abspath("cargaDatos.py"))
sys.path.insert(0, script_dir)

from carga_datos.cargaDatos import cargar_datos_base as cargar_datos
from herramientas_compartidas.distancia_haversine import haversine

def construccion_modelo(clientes, depositos, parametros, vehiculos):
    # Aquí iría la construcción del modelo de optimización usando Pyomo
    model = ConcreteModel()
    
    # Definición de conjuntos
    #Clientes
    model.C = Set(initialize=clientes['StandardizedID'].tolist())
    #Depósitos
    model.D = Set(initialize=depositos['StandardizedID'].tolist())
    #Vehículos
    model.V = Set(initialize=vehiculos['StandardizedID'].tolist())
    # Nodos
    model.N = model.C | model.D
    
    # Definición de parámetros
    #distancias entre nodos
    distancia_dict = {}
    #primero de los centros de distribucion a todos los clientes
    for i in model.D:
        dlongitud= depositos.loc[depositos['StandardizedID'] == i, 'Longitude'].values[0]
        dlatitud= depositos.loc[depositos['StandardizedID'] == i, 'Latitude'].values[0]
        for j in model.C:
            clongitud= clientes.loc[clientes['StandardizedID'] == j, 'Longitude'].values[0]
            clatitud= clientes.loc[clientes['StandardizedID'] == j, 'Latitude'].values[0]
            distancia = haversine(dlatitud, dlongitud, clatitud, clongitud)
            distancia_dict[(i,j)] = distancia
            distancia_dict[(j,i)] = distancia # Asumiendo simetría
    #luego entre clientes
    for i in model.C:
        clongitud_i= clientes.loc[clientes['StandardizedID'] == i, 'Longitude'].values[0]
        clatitud_i= clientes.loc[clientes['StandardizedID'] == i, 'Latitude'].values[0]
        for j in model.C:
            if i != j:
                clongitud_j= clientes.loc[clientes['StandardizedID'] == j, 'Longitude'].values[0]
                clatitud_j= clientes.loc[clientes['StandardizedID'] == j, 'Latitude'].values[0]
                distancia = haversine(clatitud_i, clongitud_i, clatitud_j, clongitud_j)
                distancia_dict[(i,j)] = distancia
    model.dist=Param(model.N, model.N, initialize=distancia_dict, default=0)
    #Demandas de clientes (kg)
    model.demand=Param(model.C, initialize=clientes.set_index('StandardizedID')['Demand'].to_dict())
    #Capacidad de los vehículos (kg)
    model.cap=Param(model.V, initialize=vehiculos.set_index('StandardizedID')['Capacity'].to_dict())
    #Autonomia de los vehículos (km por tanque lleno)
    model.aut=Param(model.V, initialize=vehiculos.set_index('StandardizedID')['Range'].to_dict())
    #Costo por galon de gasolina (COP/galon)
    model.gas_cost=Param(initialize=parametros.loc[parametros['Parameter'] == 'fuel_price', 'Value'].values[0])
    #Rendimiento gasolina (km/galon)
    model.gas_eff=Param(initialize=parametros.loc[parametros['Parameter'] == 'fuel_efficiency_typical', 'Value'].values[0])
    #Velocidad promedio (km/h)
    model.avg_speed=Param(initialize=80) # Valor supuesto
    
    #Variables de decisión
    model.x = Var(model.N, model.N, model.V, domain=Binary)  # 1 si el vehículo v va de i a j
    model.y = Var(model.N, model.V, domain=NonNegativeIntegers)  # entero que representa el orden en el que el vehiculo visita el nodo
    #funcion objetivo
    def obj_rule(model):
        return sum(model.dist[i,j] * (model.gas_cost / model.gas_eff) * model.x[i,j,v] 
                   for i in model.N for j in model.N for v in model.V if i != j)
    model.OBJ = Objective(rule=obj_rule, sense=minimize)
    
    #Restricciones
    
    #Cada cliente es atendido por exactamente un vehículo
    def cliente_atendido_rule(model, c):
        return sum(model.x[i,c,v] for i in model.N for v in model.V if i != c) == 1
    model.cliente_atendido = Constraint(model.C, rule=cliente_atendido_rule)
    #Un vehiculo no puede recorrer mas distancia que su autonomia
    def autonomia_vehiculo_rule(model, v):
        return sum(model.dist[i,j] * model.x[i,j,v] for i in model.N for j in model.N if i != j) <= model.aut[v]
    model.autonomia_vehiculo = Constraint(model.V, rule=autonomia_vehiculo_rule)
    #todo vehiculo debe partir de un deposito
    def salida_deposito_rule(model, v):
        return sum(model.x[d,j,v] for d in model.D for j in model.N if j != d) == 1
    model.salida_deposito = Constraint(model.V, rule=salida_deposito_rule)
    #todo vehiculo debe regresar a un deposito
    def regreso_deposito_rule(model, v):
        return sum(model.x[i,d,v] for d in model.D for i in model.N if i != d) == 1
    model.regreso_deposito = Constraint(model.V, rule=regreso_deposito_rule)
    #Todo vehiculo que llege a un nodo que no sea deposito debe salir de ese nodo
    def flujo_nodos_rule(model, n, v):
        if n in model.D:
            return Constraint.Skip
        return sum(model.x[i,n,v] for i in model.N if i != n) == sum(model.x[n,j,v] for j in model.N if j != n)
    model.flujo_nodos = Constraint(model.N, model.V, rule=flujo_nodos_rule)
    #Eliminacion de subciclos (MTZ)
    def mtz_rule(model, i, j, v):
        if i == j or i in model.D or j in model.D:
            return Constraint.Skip
        M = len(model.C) + 1
        return model.y[i,v] - model.y[j,v] + M * model.x[i,j,v] <= M - 1
    model.mtz = Constraint(model.N, model.N, model.V, rule=mtz_rule)
    #los centros de distribucion tienen orden 0 (inicio del recorrido)
    def orden_deposito_rule(model, d, v):
        return model.y[d,v] == 0
    model.orden_deposito = Constraint(model.D, model.V, rule=orden_deposito_rule)
    #Capacidad de los vehiculos no supera la demanda de atendidos
    def capacidad_vehiculo_rule(model, v):
        return sum(model.demand[c] * model.x[i,c,v] for c in model.C for i in model.N if i != c) <= model.cap[v]
    model.capacidad_vehiculo = Constraint(model.V, rule=capacidad_vehiculo_rule)
    #Dominio de variables ya definido en la declaración
    
    return model

if __name__ == "__main__":
    # Cargar los datos
    clientes, depositos, parametros, vehiculos = cargar_datos()
    # Construir el modelo
    model = construccion_modelo(clientes, depositos, parametros, vehiculos)
    for i in model.dist:
        print(i, model.dist[i])
    # Crear el solucionador
    solver = SolverFactory('appsi_highs')  # Asegúrate de tener SCIP instalado
    # Resolver el modelo
    start_time = time.time()
    results = solver.solve(model, tee=True)
    end_time = time.time()
    print(f"Tiempo de resolución: {end_time - start_time} segundos")
    print("Estado de la solución:", results.solver.status)
    print("Condición de la solución:", results.solver.termination_condition)
    print("Valor de la función objetivo:", value(model.OBJ))
    
    

    