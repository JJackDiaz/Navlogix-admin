# myapp/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from home.models import Company, Fleet, Address, Vehicle, Route, RouteAddress, RouteVehicle

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

class RouteAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteAddress
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class FleetSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = Fleet
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = Address
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    fleet = FleetSerializer()
    user = serializers.StringRelatedField()  # Or you can use a UserSerializer if needed

    class Meta:
        model = Vehicle
        fields = '__all__'

class RouteSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer()

    class Meta:
        model = Route
        fields = '__all__'

class RouteAddressSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = RouteAddress
        fields = '__all__'
