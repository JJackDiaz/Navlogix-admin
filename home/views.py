from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import Address, Route, Driver, Vehicle, ParentItem
from .utils import optimize_and_save_routes, get_coordinates
import pandas as pd
import datetime
import json

def index(request):
    return render(request, 'pages/index.html')

def address(request):

    #INI INSERTO VEHICULOS
    #####vehicle = Vehicle(brand='Critroen', model='Corolla', plate='ABC-4456', capacity=50)
    #####vehicle.save()

    #####driver = Driver(name='Pedro', vehicle=vehicle)
    #####driver.save()
    #FIN INSERTO VEHICULOS

    today = datetime.date.today()
    routes = Route.objects.filter(parent_item__date=today)
    
    # Obtener todos los choferes disponibles
    drivers = Driver.objects.all()
    
    routes_data = [
        {
            'address': route.address.street + ' ' + route.address.number + ', ' + route.address.city,
            'longitude': route.address.longitude,
            'latitude': route.address.latitude,
            'order': route.order,
            'description': route.parent_item.description,
            'driver': route.driver.id  # Cambiado de 'drivers' a 'driver'
        }
        for route in routes
    ]
    
    return render(request, 'pages/routes/address.html', {'routes': json.dumps(routes_data), 'drivers': drivers})

def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return redirect('address')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

def handle_uploaded_file(file):
    try:
        df = pd.read_excel(file)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return

    expected_columns = ['street', 'number', 'city', 'lat', 'long']
    for col in expected_columns:
        if col not in df.columns:
            print(f"Error: Falta la columna '{col}' en el archivo.")
            return

    created_addresses = []

    for route_index, (_, row) in enumerate(df.iterrows()):
        try:
            #coordinates = get_coordinates(row['street'], row['number'], row['city'])
            #if coordinates:
                #latitude, longitude = coordinates
                latitude = row['lat'] 
                longitude = row['long']
                address = Address.objects.create(
                    street=row['street'], 
                    number=row['number'],
                    city=row['city'],
                    latitude=latitude,
                    longitude=longitude
                )
                created_addresses.append(address)
            #else:
            #    print(f"Error: No se pudieron obtener las coordenadas para la dirección: {row['street']} {row['number']}, {row['city']}")
        except KeyError as e:
            print(f"Error: Falta la columna {e} en el archivo.")
        except Exception as e:
            print(f"Error al procesar la fila: {e}")

    vehicles = Vehicle.objects.all()
    optimize_and_save_routes(created_addresses, vehicles)

                   
