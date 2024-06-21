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