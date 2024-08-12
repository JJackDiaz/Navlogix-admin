# myapp/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from home.models import Route,Address, Vehicle

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','email','last_name')

class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = '__all__'

