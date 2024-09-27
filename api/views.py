# myapp/views.py
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import LoginSerializer, RouteSerializer, RouteAddressSerializer, CompanySerializer, FleetSerializer, AddressSerializer, VehicleSerializer, RouteSerializer, RouteAddressSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from home.models import Company, Fleet, Address, Vehicle, Route, RouteAddress, RouteVehicle

from home.models import Route
from home.models import RouteAddress

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        user = authenticate(username=username, password=password)

        if user:

            group_name = 'driver'
            user_groups = user.groups.values_list('name', flat=True)
            user_group_id = user.groups.values_list('id', flat=True)
            
            if group_name not in user_groups:
                return Response({'error': 'No tiene permiso para acceder'}, status=status.HTTP_403_FORBIDDEN)
        
            login_serializer = self.serializer_class(data=request.data, context={'request': request})

            if login_serializer.is_valid():
                token, created = Token.objects.get_or_create(user=user)
    
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email, 
                    'group': user_groups,
                    'groupid': user_group_id
                }
                return Response({
                    'token': token.key,
                    'user': user_data,
                    'message': 'Login exitoso'
                }, status=status.HTTP_200_OK)
            else:
                return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': 'Contraseña o nombre de usuario incorrectos'}, status=status.HTTP_400_BAD_REQUEST)



class Logout(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            Token.objects.get(user=user).delete()
            return Response({'message': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'error': 'El usuario no tiene un token válido.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#RUTAS POR USUARIO
class UserRoutesView(generics.ListAPIView):
    serializer_class = RouteAddressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        try:
            vehicle = Vehicle.objects.get(user_id=user_id)
        except Vehicle.DoesNotExist:
            raise Http404("Vehicle not found")

        # Get the active route for the vehicle
        user_route = Route.objects.filter(vehicle_id=vehicle.id, is_active=True).first()
        if user_route is None:
            # If there's no active route, return an empty queryset or raise an exception
            return RouteAddress.objects.none()

        # Return addresses associated with the route
        return RouteAddress.objects.filter(route_id=user_route.id)

#DETALLE RUTA
class DetailRoutesView(generics.RetrieveAPIView):
    serializer_class = RouteAddressSerializer
    permission_classes = (IsAuthenticated,)
    queryset = RouteAddress.objects.all()  # Asegúrate de que tu queryset esté configurado

    def get(self, request, *args, **kwargs):
        route_id = self.kwargs.get('route_id')
        try:
            route = self.get_object()  # Esto usará el queryset para buscar el objeto
            serializer = self.get_serializer(route)
            return Response(serializer.data)
        except RouteAddress.DoesNotExist:
            return Response({"detail": "Route not found."}, status=status.HTTP_404_NOT_FOUND)

# API para gestionar compañías
class CompanyListCreateView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

class CompanyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

# API para gestionar flotas
class FleetListCreateView(generics.ListCreateAPIView):
    queryset = Fleet.objects.all()
    serializer_class = FleetSerializer
    permission_classes = [IsAuthenticated]

class FleetRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Fleet.objects.all()
    serializer_class = FleetSerializer
    permission_classes = [IsAuthenticated]

# API para gestionar direcciones
class AddressListCreateView(generics.ListCreateAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

class AddressRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

# API para gestionar vehículos
class VehicleListCreateView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

class VehicleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

# API para gestionar rutas
class RouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

class RouteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

# API para gestionar las direcciones dentro de una ruta
class RouteAddressListCreateView(generics.ListCreateAPIView):
    queryset = RouteAddress.objects.all()
    serializer_class = RouteAddressSerializer
    permission_classes = [IsAuthenticated]

class RouteAddressRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RouteAddress.objects.all()
    serializer_class = RouteAddressSerializer
    permission_classes = [IsAuthenticated]

# API para obtener las rutas activas de un vehículo
class VehicleActiveRouteView(generics.RetrieveAPIView):
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        vehicle_id = self.kwargs.get('vehicle_id')
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            active_route = Route.objects.filter(vehicle=vehicle, is_active=True).first()
            if not active_route:
                return Response({'error': 'No active route for this vehicle'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(active_route)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Vehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)