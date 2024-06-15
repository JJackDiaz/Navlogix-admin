# myapp/models.py

from django.db import models

class Address(models.Model):
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.street}, {self.number}, {self.city}"

class Vehicle(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    plate = models.CharField(max_length=20)
    capacity = models.IntegerField(default=1)  # Añadir el campo de capacidad

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate})"

class Driver(models.Model):
    name = models.CharField(max_length=100)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

class ParentItem(models.Model):
    day = models.CharField(max_length=20)
    date = models.DateField()
    description = models.TextField()

class Route(models.Model):
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    parent_item = models.ForeignKey(ParentItem, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)

class UploadFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
