from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Fleet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='fleets')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.company.name})"

class Address(models.Model):
    title = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, null=True, blank=True)
    note = models.CharField(max_length=100)
    receives = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    latitude = models.CharField(max_length=20, default='0.0')
    longitude = models.CharField(max_length=20, default='0.0')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='addresses')

    def __str__(self):
        return f"{self.street}, {self.city} ({self.company.name})"


class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    origin_address = models.CharField(max_length=100)
    latitude = models.CharField(max_length=20, default='0.0')
    longitude = models.CharField(max_length=20, default='0.0')
    capacity = models.IntegerField(default=1)
    fleet = models.ForeignKey(Fleet, on_delete=models.CASCADE, related_name='vehicles')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

def get_today():
    return date.today()

def get_day():
    return date.today().strftime('%A')

def get_description():
    return f"Item de {date.today()}"

class Route(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    created_at = models.CharField(max_length=20)

    def __str__(self):
        return self.name

# Tabla para asociar vehículos con rutas
class RouteVehicle(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('route', 'vehicle')

# Tabla para asociar direcciones con rutas
class RouteAddress(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    order = models.IntegerField()

    # Estado del punto (e.g., pending, in progress, completed, canceled)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ], default='pending', null=True, blank=True)

    delivery_date = models.DateField(null=True, blank=True, default=None)
    alert_time = models.TimeField(null=True, blank=True, default=None)
    photo = models.ImageField(upload_to='route_photos/', null=True, blank=True, default=None)
    note = models.TextField(null=True, blank=True, default=None)
    estimated_arrival_time = models.TimeField(null=True, blank=True, default=None)
    departure_time = models.TimeField(null=True, blank=True, default=None)
    recipient_name = models.CharField(max_length=255, null=True, blank=True, default=None)
    recipient_signature = models.ImageField(upload_to='signatures/', null=True, blank=True, default=None)
    time_window_start = models.TimeField(null=True, blank=True, default=None)
    time_window_end = models.TimeField(null=True, blank=True, default=None)

    class Meta:
        unique_together = ('route', 'address')
        ordering = ['order']


class UploadFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='upload_files')

    def __str__(self):
        return f"Upload {self.id} - {self.company.name} at {self.uploaded_at}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users')

    def __str__(self):
        return f"{self.user.username} - {self.company.name}"
