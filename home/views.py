from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import Address, Route, Driver, Vehicle, ParentItem
from .utils import optimize_and_save_routes, get_coordinates
import pandas as pd
import datetime
import json
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from .forms_steps import Step1Form, Step2Form, Step3Form

@login_required
def index(request):
    return render(request, 'pages/index.html')

@login_required
def planning(request):

    step1_form = Step1Form()
    step2_form = Step2Form()
    step3_form = Step3Form()
    
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
    
    context = {
        'step1_form': step1_form,
        'step2_form': step2_form,
        'step3_form': step3_form,
        'routes': json.dumps(routes_data),
        'drivers': drivers,
    }
    
    return render(request, 'pages/planning/address.html', context)

def save_step_data(request, step):

    print(request,step)
    if request.method == 'POST':
        if step == 1:
            selected_drivers = request.POST.getlist('drivers')
            print(selected_drivers)
            request.session['selected_drivers'] = selected_drivers
            return JsonResponse({'status': 'success'})
        elif step == 2:
            if(request.session.get('uploaded_addresses')):
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid step'})
        elif step == 3:
            form = Step3Form(request.POST)
            if form.is_valid():
                request.session[f'step{step}_data'] = form.cleaned_data
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid step'})

        if form.is_valid():
            request.session[f'step{step}_data'] = form.cleaned_data
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
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

#--------------- VALIDACION FORMULARIO 3 PASOS ------------------------

def upload_routes(request, step):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        addresses = process_uploaded_file(uploaded_file)

        request.session['uploaded_addresses'] = addresses

        return JsonResponse({'status': 'success', 'addresses': addresses})
    else:
        return JsonResponse({'status': 'error', 'message': 'No se recibió ningún archivo o método incorrecto'})

def process_uploaded_file(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file)
        addresses = df['street'].astype(str) + ' ' + df['number'].astype(str) + ', ' + df['city'].astype(str)
        addresses_list = addresses.tolist()

        return addresses_list
    except Exception as e:
        print('Error al procesar el archivo:', str(e))
        return []

def complete_form(request):
    try:

        step1_data = request.session.get('selected_drivers')
        step2_data = request.session.get('uploaded_addresses')

        print(step1_data)
        print(step2_data)
        
        return JsonResponse({'status': 'success', 'message': 'Formulario completado exitosamente.'})
    except Exception as e:
        print(f'Error al completar el formulario: {str(e)}')
        return JsonResponse({'status': 'error', 'message': 'Error al procesar el formulario. Por favor, inténtalo de nuevo más tarde.'})