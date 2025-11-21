import math
import requests
import pandas as pd
def haversine(lat1, lon1, lat2, lon2):
    # Radio de la Tierra en kilómetros
    R = 6371 

    # Convertir grados a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Diferencia en latitud y longitud
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Fórmula de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance

def osrm_distance(p1, p2) -> float:
        """Calculate distance using OSRM API."""
 

        url = f"http://router.project-osrm.org/route/v1/driving/{p1[0]},{p1[1]};{p2[0]},{p2[1]}?annotations=duration,distance"

        try:
            response = requests.get(url)
            data = response.json()

            if "routes" in data and len(data["routes"]) > 0:
                # Distance in meters, convert to kilometers
                distancia = data["routes"][0]["distance"] / 1000
                duracion = data["routes"][0]["duration"] / 60  # duration in minutes
            else:
                distancia= haversine(p1[1], p1[0], p2[1], p2[0])
                duracion=distancia/80*60  # assuming average speed of 80 km/h
            
            return distancia, duracion
        except Exception as e:
            distancia= haversine(p1[1], p1[0], p2[1], p2[0])
            duracion=distancia/80*60  # assuming average speed of 80 km
            return distancia, duracion

def gen_csv_distancia_tiempo (nom_archivo, clientes, depositos):
    # Genera un archivo CSV con las distancias y tiempos entre nodos usando OSRM para cualquier caso
    dict_archivo={
        "FromID":[],
        "ToID":[],
        "Distance_km":[],
        "Time_min":[]
    }
    for i, fila_i in clientes.iterrows():
        for j, fila_j in clientes.iterrows():
            if i != j:
                dist, time = osrm_distance(
                    (fila_i["Longitude"], fila_i["Latitude"]),
                    (fila_j["Longitude"], fila_j["Latitude"])
                )
                dict_archivo["FromID"].append(fila_i["StandardizedID"])
                dict_archivo["ToID"].append(fila_j["StandardizedID"])
                dict_archivo["Distance_km"].append(dist)
                dict_archivo["Time_min"].append(time)
    for i, fila_i in depositos.iterrows():
        for j, fila_j in clientes.iterrows():
            dist, time = osrm_distance(
                (fila_i["Longitude"], fila_i["Latitude"]),
                (fila_j["Longitude"], fila_j["Latitude"])
            )
            dict_archivo["FromID"].append(fila_i["StandardizedID"])
            dict_archivo["ToID"].append(fila_j["StandardizedID"])
            dict_archivo["Distance_km"].append(dist)
            dict_archivo["Time_min"].append(time)
    df_distancias = pd.DataFrame(dict_archivo)
    df_distancias.to_csv(nom_archivo, index=False)