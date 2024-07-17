# myapp/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','email','last_name')
