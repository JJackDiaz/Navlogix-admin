from django.db import models
from django.contrib.auth.models import User
from datetime import date

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
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    latitude = models.CharField(max_length=20, default='0.0')
    longitude = models.CharField(max_length=20, default='0.0')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='addresses')

    def __str__(self):
        return f"{self.street}, {self.number}, {self.city} ({self.company.name})"

class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    origin_address = models.CharField(max_length=100)
    latitude = models.CharField(max_length=20, default='0.0')
    longitude = models.CharField(max_length=20, default='0.0')
    capacity = models.IntegerField(default=1)
    fleet = models.ForeignKey(Fleet, on_delete=models.CASCADE, related_name='vehicles')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return {self.fleet.name}

def get_today():
    return date.today()

def get_day():
    return date.today().strftime('%A')

def get_description():
    return "Item de ",date.today()

class ParentItem(models.Model):
    day = models.CharField(max_length=20, default=get_day)
    date = models.DateField(default=get_today)
    description = models.TextField(default=get_description)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='parent_items')

    def __str__(self):
        return f"{self.day}, {self.date} - {self.company.name}"

class Route(models.Model):
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    latitude = models.CharField(max_length=20, default='0.0')
    longitude = models.CharField(max_length=20, default='0.0')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='routes')
    parent_item = models.ForeignKey(ParentItem, on_delete=models.CASCADE, related_name='routes')
    order = models.CharField(max_length=100)

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
