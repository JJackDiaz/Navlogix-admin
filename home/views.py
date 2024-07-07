from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import Address, Route, Driver, Vehicle, ParentItem
from .utils import optimize_and_save_routes
import pandas as pd
import datetime
import json
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404

from django.http import HttpResponse, JsonResponse
from .forms_steps import Step1Form, Step2Form
from django.contrib.sessions.backends.db import SessionStore

@login_required
def index(request):
    return render(request, 'pages/index.html')

@login_required
def planning(request):
    step1_form = Step1Form()
    step2_form = Step2Form()
    #step3_form = Step3Form()
    
    today = datetime.date.today()
    routes = Route.objects.filter(parent_item__date=today)
    
    drivers = Driver.objects.all()
    
    routes_data = [
        {
            'address': route.address.street + ' ' + route.address.number + ', ' + route.address.city,
            'longitude': route.address.longitude,
            'latitude': route.address.latitude,
            'order': route.order,
            'description': route.parent_item.description,
            'driver': route.driver.id
        }
        for route in routes
    ]
    
    context = {
        'step1_form': step1_form,
        'step2_form': step2_form,
        'routes': json.dumps(routes_data),
        'drivers': drivers,
    }
    
    return render(request, 'pages/planning/address.html', context)

@login_required
def save_step_data(request, step):
    if request.method == 'POST':
        if step == 1:
            selected_vehicle_ids = request.POST.getlist('drivers')
            
            if selected_vehicle_ids:
                # Consultar los objetos completos de los vehículos seleccionados
                selected_vehicles = Vehicle.objects.filter(id__in=selected_vehicle_ids)

                # Guardar los objetos completos de los vehículos en la sesión
                request.session['selected_drivers'] = list(selected_vehicles.values())

                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Selecciona un chofer'})
        elif step == 2:
            uploaded_addresses = request.session.get('uploaded_addresses')
            if uploaded_addresses:
                create_routes(request)
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid step'})
        else:
            if request.session.get('optimized_routes'):
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            try:
                df = pd.read_excel(uploaded_file)
            except Exception as e:
                print(f"Error al leer el archivo: {e}")
                return HttpResponseBadRequest("Error al leer el archivo")

            expected_columns = ['street', 'number', 'city', 'lat', 'long']
            for col in expected_columns:
                if col not in df.columns:
                    print(f"Error: Falta la columna '{col}' en el archivo.")
                    return HttpResponseBadRequest(f"Falta la columna '{col}' en el archivo")

            request.session['uploaded_addresses'] = df.to_dict(orient='records')
            return JsonResponse({'status': 'success', 'addresses': df.to_dict(orient='records')})
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

@login_required
def upload_routes(request, step):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            try:
                df = pd.read_excel(uploaded_file)
            except Exception as e:
                print(f"Error al leer el archivo: {e}")
                return HttpResponseBadRequest("Error al leer el archivo")

            expected_columns = ['street', 'number', 'city', 'lat', 'long']
            for col in expected_columns:
                if col not in df.columns:
                    print(f"Error: Falta la columna '{col}' en el archivo.")
                    return HttpResponseBadRequest(f"Falta la columna '{col}' en el archivo")

            request.session['uploaded_addresses'] = df.to_dict(orient='records')
            return JsonResponse({'status': 'success', 'addresses': df.to_dict(orient='records')})
    return JsonResponse({'status': 'error', 'message': 'No se recibió ningún archivo o método incorrecto'})

@login_required
def get_session_data(request):
    session_key = 'optimized_routes'
    session_id = request.session.session_key

    try:
        db_session = Session.objects.get(session_key=session_id)
        session_data = db_session.get_decoded().get(session_key, {})
        return JsonResponse(session_data)
    except Session.DoesNotExist:
        return JsonResponse({'error': 'No se encontró la sesión'}, status=404)

@login_required
def create_routes(request):
    step1_data = request.session.get('selected_drivers')

    print(step1_data)

    if not step1_data:
        return JsonResponse({'status': 'error', 'message': 'Selected drivers not found in session'}, status=400)
    
    created_addresses = request.session.get('uploaded_addresses', [])
    if not created_addresses:
        return JsonResponse({'status': 'error', 'message': 'No addresses found'}, status=400)
    
    vehicles = Vehicle.objects.all()
    result = optimize_and_save_routes(created_addresses, step1_data)

    if 'error' in result:
        return JsonResponse({'status': 'error', 'message': result['error']}, status=400)


    request.session['optimized_routes'] = result

    print("Rutas optimizadas almacenadas en la sesión:", request.session.get('optimized_routes'))
    
    return JsonResponse({'status': 'success', 'addresses': created_addresses})

@login_required
def show_routes(request):
    # Obtener los datos guardados en la sesión
    step2_data = request.session.get('uploaded_addresses')

    if not step2_data:
        return JsonResponse({'status': 'error', 'message': 'Uploaded addresses not found in session'}, status=400)
    
     # Obtener las rutas optimizadas de la sesión
    session_key = 'optimized_routes'  # La clave de sesión donde se guardaron las rutas optimizadas
    session_store = SessionStore()
    
    optimized_routes = request.session['optimized_routes']
        
    return JsonResponse({'status': 'success', 'optimized_routes': optimized_routes})

@login_required
def complete_form(request):
    try:
        step1_data = request.session.get('selected_drivers')
        step2_data = request.session.get('uploaded_addresses')

        if not step1_data or not step2_data:
            raise Exception('Incomplete session data')
        
        return JsonResponse({'status': 'success', 'message': 'Formulario completado exitosamente.'})
    except Exception as e:
        print(f'Error al completar el formulario: {str(e)}')
        return JsonResponse({'status': 'error', 'message': 'Error al procesar el formulario. Por favor, inténtalo de nuevo más tarde.'})
