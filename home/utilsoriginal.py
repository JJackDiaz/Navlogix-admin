import math
from itertools import permutations
from django.db.models import Count, F
import datetime
import requests
import time

from sklearn.cluster import KMeans
import numpy as np

# Vecino cercano
from sklearn.neighbors import NearestNeighbors

from .models import Address, Route, Driver, Vehicle, ParentItem

def calculate_distance(address1, address2):
    R = 6371.0
    lat1 = math.radians(address1.latitude)
    lon1 = math.radians(address1.longitude)
    lat2 = math.radians(address2.latitude)
    lon2 = math.radians(address2.longitude)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

# ALGORITMO VECINO MAS CERCANO
def optimize_route_for_vehicle(route_addresses):
    if not route_addresses or len(route_addresses) < 2:
        return route_addresses

    # Convertir las direcciones a un array de numpy
    locations = np.array([[address.latitude, address.longitude] for address in route_addresses])

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

# ALGORITMO 2-opt
def optimize_route_for_vehicle2(route_addresses):
    if not route_addresses or len(route_addresses) < 2:
        return route_addresses

    # Convertir las direcciones a un array de numpy
    locations = np.array([[address.latitude, address.longitude] for address in route_addresses])

    # Crear el modelo NearestNeighbors
    neighbors = NearestNeighbors(n_neighbors=len(route_addresses), algorithm='ball_tree').fit(locations)

    # Inicializar la ruta con la primera dirección
    route = [route_addresses[0]]
    remaining_addresses = set(route_addresses[1:])

    while remaining_addresses:
        # Encontrar el vecino más cercano a la última dirección en la ruta
        distances, indices = neighbors.kneighbors(np.array([route[-1].latitude, route[-1].longitude]).reshape(1, -1))
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
        total_distance += np.sqrt((route[i+1].latitude - route[i].latitude)**2 + 
                                  (route[i+1].longitude - route[i].longitude)**2)
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
    coordinates = np.array([[address.latitude, address.longitude] for address in addresses])
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(coordinates)
    clustered_addresses = [[] for _ in range(n_clusters)]

    for i, label in enumerate(kmeans.labels_):
        clustered_addresses[label].append(addresses[i])

    return clustered_addresses

def optimize_and_save_routes(addresses, vehicles):
    drivers = Driver.objects.annotate(num_routes=Count('route')).filter(num_routes__lt=F('vehicle__capacity'))

    if not drivers.exists():
        print("No hay conductores disponibles para asignar rutas.")
        return

    if not addresses or not vehicles:
        print("La lista de direcciones o vehículos está vacía.")
        return

    start_time = time.time()

    today = datetime.date.today()
    Route.objects.filter(parent_item__date=today).delete()

    n_clusters = len(vehicles)
    clustered_addresses = cluster_addresses(addresses, n_clusters)

    vehicle_routes = {vehicle: [] for vehicle in vehicles}

    for i, cluster in enumerate(clustered_addresses):
        vehicle = vehicles[i]
        vehicle_routes[vehicle] = cluster

    for vehicle, route_addresses in vehicle_routes.items():
        optimal_route = optimize_route_for_vehicle3(route_addresses)
        print(f"RUTA para {vehicle}:")
        for i, address in enumerate(optimal_route):
            order = i + 1
            print(f"  Destino {order}: {address}")
        driver = drivers.filter(vehicle=vehicle).first()

        if driver:
            for i, address in enumerate(optimal_route):
                order = i + 1
                parent_item, _ = ParentItem.objects.get_or_create(
                    day='Monday', date=today, description=f'Description {order}'
                )
                Route.objects.get_or_create(address=address, driver=driver, parent_item=parent_item, order=order)
                execution_time = time.time() - start_time
            print(f"Tiempo de ejecución: {execution_time:.4f} segundos")
        else:
            print(f"No se encontró conductor para el vehículo {vehicle}.")

def get_coordinates(street, number, city):
    MAPBOX_ACCESS_TOKEN = 'pk.eyJ1Ijoicm91dGUyNCIsImEiOiJjbHd5Z25oeWQxbDV5MnFxOHE4OGFla2o4In0.AWn6zJ26HiXyH04mIAq6Kg'
    address = f"{street} {number}, {city}"
    url = f'https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json?access_token={MAPBOX_ACCESS_TOKEN}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['features']:
            coordinates = data['features'][0]['geometry']['coordinates']
            return coordinates[1], coordinates[0]
        else:
            print(f"No se encontraron coordenadas para la dirección: {address}")
            return None
    except requests.RequestException as e:
        print(f"Error en la solicitud a Mapbox: {e}")
        return None
