from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
# Create your models here.

class DatesOfTravel(models.Model):
    first_date = models.DateField(null=False)
    second_date = models.DateField(null=False)

    class Meta:
        verbose_name = 'DateOfTravel'
        verbose_name_plural = 'DatesOfTravels'

    def __str__(self):
        return f"{self.first_date} - {self.second_date}"
    
class Bus(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    date_of_travel = models.ForeignKey(DatesOfTravel, on_delete=models.CASCADE, null=False)
    
    class Meta:
        verbose_name = 'Bus'
        verbose_name_plural = 'Buses'
    
    def __str__(self):
        return self.nombre
    
class Rooms_Bus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)

class Companions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companions')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Companion'
        verbose_name_plural = 'Companions'

    def __str__(self):
        return self.user.username

class Asiento(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    numero = models.IntegerField(null=False)
    estado = models.CharField(
        max_length=100,
        choices=[('disponible', 'Disponible'), ('reservado', 'Reservado')],
        default='disponible'
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    companion = models.ForeignKey(Companions, on_delete=models.SET_NULL, null=True, blank=True)
    companion_name = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Asiento'
        verbose_name_plural = 'Asientos'
        unique_together = ('bus', 'numero')
    
    def __str__(self):
        return f"{self.bus.nombre} - Seat {self.numero}"
    def clean(self):
        if self.user and self.estado == 'reservado':
            # Check how many seats the user has reserved already
            reserved_seats = Asiento.objects.filter(user=self.user, estado='reservado').count()
            
            # Get the user's information
            try:
                user_info = UserMoreInformation.objects.get(user=self.user)
                max_reservations = user_info.people
            except UserMoreInformation.DoesNotExist:
                max_reservations = 1  # Default to 1 if no user information is found
            
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
class UserMoreInformation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    people = models.IntegerField(null=False)
    price = models.FloatField(null=False)
    date_of_travel = models.ForeignKey(DatesOfTravel, on_delete=models.SET_NULL, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True)
    vip = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'UserMoreInformation'
        verbose_name_plural = 'UserMoreInformations'