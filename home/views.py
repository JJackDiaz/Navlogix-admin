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
            uploaded_addresses = request.session.get('uploaded_addresses')
            if uploaded_addresses:
                create_routes(uploaded_addresses)
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid step'})
        elif step == 3:
            form = Step3Form(request.POST)
            if form.is_valid():
                print("ENTRO")
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

@login_required
def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Lê o arquivo enviado
            uploaded_file = request.FILES['file']
            try:
                df = pd.read_excel(uploaded_file)
            except Exception as e:
                print(f"Error al leer el archivo: {e}")
                return HttpResponseBadRequest("Error al leer el archivo")

            # Verifica se o arquivo tem as colunas esperadas
            expected_columns = ['street', 'number', 'city', 'lat', 'long']
            for col in expected_columns:
                if col not in df.columns:
                    print(f"Error: Falta la columna '{col}' en el archivo.")
                    return HttpResponseBadRequest(f"Falta la columna '{col}' en el archivo")

            # Armazena o DataFrame na sessão
            request.session['uploaded_addresses'] = df.to_dict(orient='records')

            return JsonResponse({'status': 'success', 'addresses': df.to_dict(orient='records')})
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

#--------------- VALIDACION FORMULARIO 3 PASOS ------------------------
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

            # Armazena o DataFrame na sessão
            print(df.to_dict(orient='records'))
            request.session['uploaded_addresses'] = df.to_dict(orient='records')


            return JsonResponse({'status': 'success', 'addresses': df.to_dict(orient='records')})

    # Se não for um POST válido ou se houver erros, retorna uma resposta de erro
    return JsonResponse({'status': 'error', 'message': 'No se recibió ningún archivo o método incorrecto'})


    
def create_routes(request):


        print("createroutes")
        print(request)

        created_addresses = []
        created_addresses.append(request)

        # Chamando a função para otimizar e salvar as rotas
        vehicles = Vehicle.objects.all()
        optimize_and_save_routes(created_addresses, vehicles, request)
        

        return JsonResponse({'status': 'success', 'addresses': request})

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