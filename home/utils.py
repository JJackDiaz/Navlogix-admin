import math
import time
import datetime
import requests
import numpy as np
from django.db.models import Count, F
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from django.http import JsonResponse
from django.contrib.sessions.backends.db import SessionStore
from django.core.cache import cache

from .models import Address, Route, Driver, Vehicle

def calculate_distance(address1, address2):
    R = 6371.0
    lat1 = math.radians(address1['lat'])
    lon1 = math.radians(address1['long'])
    lat2 = math.radians(address2['lat'])
    lon2 = math.radians(address2['long'])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def optimize_route_for_vehicle(route_addresses):
    if not route_addresses or len(route_addresses) < 2:
        return route_addresses

    # Convertir las direcciones a un array de numpy
    locations = np.array([[address['lat'], address['long']] for address in route_addresses])

    # Crear el modelo NearestNeighbors
    neighbors = NearestNeighbors(n_neighbors=len(route_addresses), algorithm='ball_tree').fit(locations)

    # Inicializar la ruta con la primera dirección
    route = [route_addresses[0]]
    remaining_indices = set(range(1, len(route_addresses)))

    current_index = 0
    while remaining_indices:
        # Encontrar los vecinos más cercanos a la última dirección en la ruta
        distances, indices = neighbors.kneighbors(locations[current_index].reshape(1, -1), n_neighbors=len(route_addresses))
        for idx in indices[0][1:]:
            if idx in remaining_indices:
                route.append(route_addresses[idx])
                remaining_indices.remove(idx)
                current_index = idx
                break

    return route

def optimize_route_for_vehicle2(route_addresses):
    if not route_addresses or len(route_addresses) < 2:
        return route_addresses

    # Convertir las direcciones a un array de numpy
    locations = np.array([[address['lat'], address['long']] for address in route_addresses])

    # Crear el modelo NearestNeighbors
    neighbors = NearestNeighbors(n_neighbors=len(route_addresses), algorithm='ball_tree').fit(locations)

    # Inicializar la ruta con la primera dirección
    route = [route_addresses[0]]
    remaining_addresses = set(route_addresses[1:])

    while remaining_addresses:
        # Encontrar el vecino más cercano a la última dirección en la ruta
        distances, indices = neighbors.kneighbors(np.array([route[-1]['lat'], route[-1]['long']]).reshape(1, -1))
        for idx in indices[0][1:]:
            nearest_address = route_addresses[idx]
            if nearest_address in remaining_addresses:
                route.append(nearest_address)
                remaining_addresses.remove(nearest_address)
                break

    # Aplicar la optimización 2-opt
    optimized_route = two_opt(route)
    
    return optimized_route

def calculate_total_distance(route):
    total_distance = 0.0
    for i in range(len(route) - 1):
        total_distance += calculate_distance(route[i], route[i + 1])
    return total_distance

def two_opt(route):
    best_route = route[:]
    best_distance = calculate_total_distance(best_route)
    improved = True

    while improved:
        improved = False
        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route)):
                if j - i == 1:
                    continue
                new_route = best_route[:i] + best_route[i:j][::-1] + best_route[j:]
                new_distance = calculate_total_distance(new_route)
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True
    
    return best_route

from sklearn.cluster import KMeans
import numpy as np

def cluster_addresses(addresses, n_clusters):
    # Obtener la cantidad total de direcciones disponibles
    total_addresses = sum(len(lista_direcciones) for lista_direcciones in addresses)

    # Asegurar que el número de clusters no sea mayor que el número total de direcciones
    n_clusters = min(n_clusters, total_addresses)

    coordinates = []

    # Iterar sobre cada lista de direcciones
    for lista_direcciones in addresses:
        
        # Asegurarse de que direccion sea un diccionario válido
        if isinstance(lista_direcciones, dict):
            # Extraer latitud y longitud si están presentes
            latitud = lista_direcciones.get('lat')
            longitud = lista_direcciones.get('long')
            if latitud is not None and longitud is not None:
                coordinates.append([latitud, longitud])
            else:
                print(f"Advertencia: Dirección incompleta sin coordenadas: {direccion}")
    
    print("CORDINATES2", coordinates)

    # Convertir a array numpy si hay coordenadas válidas
    if coordinates:
        coordinates = np.array(coordinates)

        # Aplicar KMeans para clusterizar las coordenadas
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(coordinates)
        clustered_addresses = [[] for _ in range(n_clusters)]

        # Asignar cada dirección al cluster correspondiente según KMeans
        for direccion in addresses:
            latitud = direccion.get('lat')
            longitud = direccion.get('long')
            if latitud is not None and longitud is not None:
                # Obtener el cluster asignado por KMeans para esta dirección
                label = kmeans.predict([[latitud, longitud]])[0]
                # Agregar la dirección al cluster correspondiente
                clustered_addresses[label].append({
                    'street': direccion.get('street', ''),
                    'number': direccion.get('number', ''),
                    'lat': latitud,
                    'long': longitud
                })

        return clustered_addresses
    else:
        print("Advertencia: No se encontraron coordenadas válidas en las direcciones proporcionadas.")
        return [[] for _ in range(n_clusters)]



def optimize_and_save_routes(addresses, vehicles):
    # Verificar la disponibilidad de conductores
    drivers = Driver.objects.annotate(num_routes=Count('route')).filter(num_routes__lt=F('vehicle__capacity'))

    print("DIRECCCIONES",addresses)

    if not drivers.exists():
        print("No hay conductores disponibles para asignar rutas.")
        return {'error': 'No hay conductores disponibles para asignar rutas'}

    if not addresses or not vehicles:
        print("La lista de direcciones o vehículos está vacía.")
        return {'error': 'La lista de direcciones o vehículos está vacía'}

    start_time = time.time()

    # Calcular el número de clusters
    n_clusters = len(vehicles)
    print("NUMERO",n_clusters)
    clustered_addresses = cluster_addresses(addresses, n_clusters)

    # Crear un diccionario vacío para almacenar las rutas de los vehículos
    vehicle_routes = {vehicle['id']: [] for vehicle in vehicles}

    print(clustered_addresses)

    for i, cluster in enumerate(clustered_addresses):
        vehicle_id = vehicles[i]['id']
        vehicle_routes[vehicle_id] = cluster

    session_key = 'optimized_routes'  # Clave para almacenar en la sesión

    optimized_routes = {}

    for vehicle_id, route_addresses in vehicle_routes.items():
        optimal_route = optimize_route_for_vehicle(route_addresses)
        print(f"RUTA para vehículo ID {vehicle_id}:")
        for i, address in enumerate(optimal_route):
            order = i + 1
            print(f"  Destino {order}: {address['street']} {address['number']}, ({address['lat']}, {address['long']})")

        optimized_routes[str(vehicle_id)] = optimal_route  # Asignar las rutas optimizadas directamente


    execution_time = time.time() - start_time
    print(f"Tiempo de ejecución: {execution_time:.4f} segundos")

    return JsonResponse({'status': 'success', 'routes': optimized_routes})





