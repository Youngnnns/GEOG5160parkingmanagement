from django.contrib.auth.models import User, PermissionsMixin
from django.contrib.gis.db import models


# Create your models here.
# parking/models.py

class PublicParkingPricingModel1(models.Model):
    objectid = models.IntegerField()
    parking_name = models.CharField(max_length=100)
    day_of_week = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    fixed = models.BooleanField()


class PublicParkingPricingModel2(models.Model):
    objectid = models.IntegerField()
    parking_name = models.CharField(max_length=100)
    period_type = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


class PublicParkingPricingModel3(models.Model):
    objectid = models.IntegerField()
    parking_name = models.CharField(max_length=100)
    day_of_week = models.CharField(max_length=100)
    duration_hours = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


class PublicParkingPricingModel4(models.Model):
    objectid = models.IntegerField()
    parking_name = models.CharField(max_length=100)
    day_of_week = models.CharField(max_length=100)
    duration_hours = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


class ParkingLot(models.Model):
    objectid = models.AutoField(primary_key=True)
    car_park_name = models.CharField(max_length=100, null=True, blank=True)
    street_name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    capacity = models.IntegerField()
    available_spaces = models.IntegerField()
    maximum_stay = models.CharField(max_length=50, null=True, blank=True)
    charges = models.CharField(max_length=100, null=True, blank=True)
    electric_or_hydrogen_or_hybrid = models.CharField(max_length=100, null=True, blank=True)
    petrol_vehicles_registered_from_2005 = models.CharField(max_length=100, null=True, blank=True)
    diesel_vehicles_registered_from_2015 = models.CharField(max_length=100, null=True, blank=True)
    other_vehicles = models.CharField(max_length=100, null=True, blank=True)
    saturday_am_price = models.CharField(max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    lot_type = models.CharField(max_length=50, choices=[('roadside', 'Roadside'), ('public', 'Public')])
    location = models.GeometryField()

    def __str__(self):
        return str(self.objectid)


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    vehicle_type = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    first_name = models.CharField(max_length=100, blank=True, null=True)  # New field
    last_name = models.CharField(max_length=100, blank=True, null=True)  # New field
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # New field
    license_plate = models.CharField(max_length=20, blank=True, null=True)  # New field
    email = models.EmailField(max_length=254, blank=True, null=True)  # New field

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.parking_lot.objectid} - {self.start_time} to {self.end_time}"

