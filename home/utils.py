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

from .models import Address, Route, Vehicle
from django.contrib.auth.models import User

from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import haversine_distances

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
    remaining_addresses = route_addresses[1:]

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

def cluster_addresses(addresses, n_clusters):
    coordinates = np.array([[address['lat'], address['long']] for address in addresses])
    radians = np.radians(coordinates)
    distances = haversine_distances(radians)

    # DBSCAN puede no dar exactamente `n_clusters` clusters, ajustar `eps` y `min_samples` según sea necesario
    db = DBSCAN(eps=0.01, min_samples=1, metric='precomputed')
    labels = db.fit_predict(distances)
    
    # Map labels to clusters
    unique_labels = np.unique(labels)
    if len(unique_labels) < n_clusters:
        n_clusters = len(unique_labels)
    
    # Crear lista de listas para clusters
    clustered_addresses = [[] for _ in range(n_clusters)]
    for i, label in enumerate(labels):
        cluster_index = min(label, n_clusters - 1)  # Asegurarse de no exceder el número de clusters
        clustered_addresses[cluster_index].append(addresses[i])

    return clustered_addresses

def optimize_and_save_routes(addresses, vehicles):
    if not addresses or not vehicles:
        return {'error': 'La lista de direcciones o vehículos está vacía'}

    start_time = time.time()

    n_clusters = len(vehicles)
    clustered_addresses = cluster_addresses(addresses, n_clusters)

    vehicle_routes = {vehicle['id']: [] for vehicle in vehicles}

    for i, cluster in enumerate(clustered_addresses):
        if i < n_clusters:
            vehicle_id = vehicles[i]['id']
            vehicle_routes[vehicle_id] = cluster

    optimized_routes = {}

    for vehicle_id, route_addresses in vehicle_routes.items():
        optimal_route = optimize_route_for_vehicle(route_addresses)
        vehicle_route_with_order = []

        for i, address in enumerate(optimal_route):
            order = i + 1
            address_with_order = {
                'vehicle_id': vehicle_id,
                'order': order,
                'street': address['street'],
                'number': address['number'],
                'lat': address['lat'],
                'long': address['long']
            }
            vehicle_route_with_order.append(address_with_order)

        optimized_routes[str(vehicle_id)] = vehicle_route_with_order

    execution_time = time.time() - start_time
    print(f"Tiempo de ejecución: {execution_time:.4f} segundos")

    return {'status': 'success', 'routes': optimized_routes}






