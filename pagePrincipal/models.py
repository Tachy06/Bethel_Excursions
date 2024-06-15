from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError

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
    number = models.CharField(max_length=10, unique=True)  # Número o identificador único del cuarto
    max_capacity = models.PositiveIntegerField(default=4)  # Capacidad máxima de 4 personas
    min_capacity = models.PositiveIntegerField(default=1)  # Capacidad mínima de 1 persona
    remaining_spaces = models.IntegerField(default=4)  # Espacios restantes del cuarto

    class Meta:
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'

    def __str__(self):
        return f"Room {self.number} (Capacity: {self.min_capacity}-{self.max_capacity})"
    

class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)  # Relación con el cuarto
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario que hace la reserva
    start_date = models.DateField()  # Fecha de inicio de la reserva
    end_date = models.DateField()  # Fecha de fin de la reserva
    number_of_people = models.PositiveIntegerField()  # Número de personas para la reserva
    exclusive = models.BooleanField(default=False)  # Si el usuario quiere exclusividad del cuarto

    def clean(self):
        # Validar que el número de personas esté dentro de la capacidad del cuarto
        if not (self.room.min_capacity <= self.number_of_people <= self.room.max_capacity):
            raise ValidationError(f"El número de personas debe estar entre {self.room.min_capacity} y {self.room.max_capacity}.")

    def __str__(self):
        return f"Reservation for Room {self.room.number} by {self.user.email} from {self.start_date} to {self.end_date}"