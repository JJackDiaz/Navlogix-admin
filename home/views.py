from django.shortcuts import render, redirect
from .forms import UploadFileForm, CompanyForm, UserProfileCreationForm
from .models import Address, Route, Driver, Vehicle, ParentItem, Company , UserProfile, Fleet
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

#ROLES
from .decorators import group_required

#groups = ['admin', 'driver', 'user']

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
    
    step2_data = request.session.get('uploaded_addresses')

    if not step2_data:
        return JsonResponse({'status': 'error', 'message': 'Uploaded addresses not found in session'}, status=400)
    
    session_key = 'optimized_routes'  # La clave de sesión donde se guardaron las rutas optimizadas
    session_store = SessionStore()
    
    optimized_routes = request.session['optimized_routes']
        
    return JsonResponse({'status': 'success', 'optimized_routes': optimized_routes})

@login_required
def complete_form(request):
    try:
        step1_data = request.session.get('selected_drivers')
        step2_data = request.session.get('uploaded_addresses')
        step3_data = request.session.get('optimized_routes')

        print("ADDRESS", step2_data)
        print("ROUTE", step3_data)

        if not step1_data or not step2_data:
            raise Exception('Incomplete session data')

        for address in step2_data:
            save_data = Address(
                street=address['street'],
                number=address['number'],
                city=address['city'],
                latitude=address['lat'],
                longitude=address['long']
            )
            save_data.save()
        
        return JsonResponse({'status': 'success', 'message': 'Formulario completado exitosamente.'})
    except Exception as e:
        print(f'Error al completar el formulario: {str(e)}')
        return JsonResponse({'status': 'error', 'message': 'Error al procesar el formulario. Por favor, inténtalo de nuevo más tarde.'})

#FLOTAS
@login_required
def fleets_index(request):
    fleets = Fleet.objects.all()
    context = {
        'fleets': fleets,
    }
    return render(request, 'pages/fleet/index.html', context)

@login_required
def fleets_detail(request, id):
    fleet = get_object_or_404(Fleet, id=id)
    vehicles = Vehicle.objects.filter(fleet=fleet)
    context = {
        'fleet': fleet,
        'vehicles': vehicles,
    }
    return render(request, 'pages/fleet/show.html', context)

#COMPANIES

@login_required
def companies_index(request):
    companies = Company.objects.all()
    context = {
        'companies': companies,
    }
    return render(request, 'pages/companies/index.html', context)

@login_required
def company_detail(request, id):
    company = get_object_or_404(Company, id=id)
    context = {
        'company': company,
    }
    return render(request, 'pages/companies/show.html', context)

@login_required
def company_delete(request, id):
    company = get_object_or_404(Company, id=id)
    if request.method == 'POST':
        company.delete()
        return redirect('companies_index')
    context = {
        'company': company,
    }
    return render(request, 'pages/companies/confirm_delete.html', context)

@login_required
def company_create(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('companies_index')
    else:
        form = CompanyForm()
    context = {
        'form': form,
    }
    return render(request, 'pages/companies/create.html', context)

@login_required
@group_required('admin')
def company_users(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    users = UserProfile.objects.filter(company=company)
    context = {
        'company': company,
        'users': users,
    }
    return render(request, 'pages/companies/users.html', context)

@login_required
@group_required('admin')
def user_create(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    if request.method == 'POST':
        form = UserProfileCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_users', company_id=company.id)
    else:
        form = UserProfileCreationForm(initial={'company': company})

    context = {
        'form': form,
        'company': company,
    }
    return render(request, 'pages/companies/user_create.html', context)


def no_permission(request):
    return render(request, 'no_permission.html')
    

