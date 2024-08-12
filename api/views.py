# myapp/views.py
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import LoginSerializer, RouteSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from home.models import Vehicle

from home.models import Route

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


class UserRoutesView(generics.ListAPIView):
    serializer_class = RouteSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.kwargs['user_id']

        vehicle = Vehicle.objects.filter(user_id=user_id).first()
        if vehicle:
            return Route.objects.filter(vehicle_id=vehicle.id)
