from django.db import models
from django.contrib.auth.models import User


class Ride(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    status = models.CharField(max_length=50, default='open')
    destination = models.CharField(max_length=150)
    arrival_time = models.TimeField()
    shareable = models.BooleanField(default=False)
    passengers_requested = models.IntegerField(default=1)
    vehicle_type_requested = models.CharField(max_length=150, blank=True)
    rider_owner_user_id = models.IntegerField()
    rider_sharer_user_id = models.IntegerField(default=0)
    driver_user_id = models.IntegerField(default=0)
    def __str__(self):
        return "Status: {} | " \
               "Rider Owner ID: {} | " \
               "Driver ID: {} | " \
               "Destination: {} | " \
               "Arrival Time {} | " \
               "Requested Vehicle Model {} | " \
               "Requested Passengers {} \n".format(
            self.status,
            self.rider_owner_user_id,
            self.driver_user_id,
            self.destination,
            self.arrival_time,
            self.vehicle_type_requested,
            self.passengers_requested)



class RideShareUser(User):
    user_type = models.CharField(max_length=150, unique=False, default='Rider Owner')



class UserSelection(models.Model):
    user_type = models.CharField(max_length=150, primary_key=True, default='Rider Owner')


class DriverUser(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    passenger_seats_in_car = models.IntegerField(default=0)
    license_plate_num = models.CharField(max_length=20)
    vehicle_model = models.CharField(max_length=20)
    def __str__(self):
        return "Driver ID: {} | Passengers: {} | License Plate Num {} | Vehicle Model {}\n".format(self.user.id, self.passenger_seats_in_car, self.license_plate_num, self.vehicle_model)


class RiderUser(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    active_ride = models.OneToOneField(Ride, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=150, default='Rider Owner')
