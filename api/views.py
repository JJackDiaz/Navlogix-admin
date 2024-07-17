# myapp/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import LoginSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

class CORSMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "*"

        return response

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        user = authenticate(username=username, password=password)

        if user:
            login_serializer = self.serializer_class(data=request.data, context={'request': request})

            if login_serializer.is_valid():
                token, created = Token.objects.get_or_create(user=user)
                # Aquí puedes incluir más información del usuario según tus necesidades
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,  # Por ejemplo, puedes agregar más campos aquí
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

        
