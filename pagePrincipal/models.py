from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from pageLogin.models import *

# Create your models here.
class Prices(models.Model):
    price = models.FloatField(null=False)
    people = models.IntegerField(null=False)
    total = models.FloatField(null=False)

    class Meta:
        verbose_name = 'Price'
        verbose_name_plural = 'Prices'
        
    def __str__(self):
        return str(self.total)

class Room(models.Model):
    number = models.CharField(max_length=10, null=True, blank=True)
    max_capacity = models.PositiveIntegerField(default=4)
    min_capacity = models.PositiveIntegerField(default=1)
    remaining_spaces = models.IntegerField(default=4)
    users = models.ManyToManyField(User, blank=True)
    companions = models.ManyToManyField(Companions, blank=True)
    rooms_bus = models.ForeignKey(Rooms_Bus, on_delete=models.CASCADE)
    

class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)  # Relación con el cuarto
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Relación con el usuario que hace la reserva
    companion = models.ForeignKey(Companions, on_delete=models.SET_NULL, null=True, blank=True)
    companion_name = models.CharField(max_length=100, null=True, blank=True)