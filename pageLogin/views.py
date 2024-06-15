from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth import login, logout, authenticate
from django.db import transaction
from pagePrincipal.models import *
from upload_Voucher.models import *

class registerView(View):
    def get(self, request):
        buses = Bus.objects.all()
        asientos_disponibles = {bus.nombre: Asiento.objects.filter(bus=bus) for bus in buses}
        fechas = DatesOfTravel.objects.all()
        rooms = Room.objects.all()
        return render(request, 'register.html', {'asientos': asientos_disponibles, 'dates': fechas, 'rooms': rooms})
    
    def post(self, request):
        first_name = request.POST['first_name']
        first_last_name = request.POST['first_last_name']
        second_last_name = request.POST['second_last_name']
        last_name = f"{first_last_name} {second_last_name}"
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        people = int(request.POST['people'])
        number_rooms = int(request.POST['rooms'])  # Cantidad de habitaciones seleccionadas
        room_ids = request.POST.getlist('number_room')  # IDs de las habitaciones seleccionadas
        seat_numbers = request.POST.getlist('seat_numbers')
        dates = request.POST['dates']
        radioVip = request.POST.get('RadioVip')
        person1 = request.POST.get('person1')
        person2 = request.POST.get('person2')
        person3 = request.POST.get('person3')

        if not room_ids:
            messages.error(request, 'Selecciona al menos una habitación')
            return redirect('/register/')

        if len(room_ids) != number_rooms:
            messages.error(request, 'El número de habitaciones seleccionadas no coincide con el número indicado')
            return redirect('/register/')

        # Verificar disponibilidad y exclusividad de habitaciones
        total_spaces_needed = people
        for room_id in room_ids:
            room = Room.objects.get(id=room_id)
            if radioVip == "Yes" and room.remaining_spaces < room.max_capacity:
                messages.error(request, f'No puedes reservar la habitación {room.number} como exclusiva porque ya tiene reservas')
                return redirect('/register/')
            if people > room.remaining_spaces:
                messages.error(request, f'No hay suficientes espacios en la habitación {room.number}')
                return redirect('/register/')
            total_spaces_needed -= room.remaining_spaces

        if total_spaces_needed > 0:
            messages.error(request, 'No hay suficientes espacios en las habitaciones seleccionadas')
            return redirect('/register/')

        if not seat_numbers:
            messages.error(request, 'Selecciona un asiento disponible')
            return redirect('/register/')
        
        if len(seat_numbers) > people:
            message = f"El usuario {username} no puede reservar más de {people} asiento(s)"
            button = "Redirigir a Registrar"
            redirectURL = '/register/'
            return render(request, 'error.html', {'message': message, 'button': button, 'redirect': redirectURL})
        
        try:
            User.objects.get(username=username)
            messages.error(request, 'Usuario ya registrado')
            return redirect('/register/')
        except User.DoesNotExist:
            pass

        try:
            with transaction.atomic():
                # Determinar precio y exclusividad
                if people > 1:
                    if radioVip == "Yes":
                        price = Prices.objects.get(people=4).total
                        vip = True
                        if number_rooms == 2:
                            price = price * 2
                    else:
                        price = Prices.objects.get(people=people).total
                        vip = False
                        if number_rooms == 2:
                            price = price * 2
                else:
                    price = Prices.objects.get(people=1).price
                    vip = False
                    if number_rooms == 2:
                        price = price * 2

                fechas = DatesOfTravel.objects.get(id=dates)
                user_create = User.objects.create(first_name=first_name, last_name=last_name, username=username, email=email)
                user_create.set_password(password)
                user_create.save()
                user = User.objects.get(username=username)
                UserMoreInformation.objects.create(user=user, people=people, rooms=number_rooms, price=price, date_of_travel=fechas)
                upload = uploadVoucher.objects.create(user=user)
                if 'voucher' in request.FILES:
                    voucher = request.FILES['voucher']
                    upload.voucher = voucher
                    upload.save()
                
                # Distribuir a las personas entre las habitaciones seleccionadas
                remaining_people = people
                companions_list = [person1, person2, person3]
                people_per_room = people // number_rooms
                extra_people = people % number_rooms
                rooms_reserved = []
                
                for room_id in room_ids:
                    room = Room.objects.get(id=room_id)
                    assigned_people = people_per_room + (1 if extra_people > 0 else 0)
                    spaces = room.remaining_spaces - assigned_people
                    Reservation.objects.create(user=user, room=room, start_date=fechas.first_date, end_date=fechas.second_date, number_of_people=assigned_people, exclusive=vip)
                    if radioVip == "Yes" and room.remaining_spaces == room.max_capacity:
                        room.remaining_spaces = 0
                        room.save()
                    else:
                        room.remaining_spaces = spaces
                        room.save()
                        remaining_people -= assigned_people
                        extra_people -= 1
                        rooms_reserved.append(room_id)
                
                if people > 1:
                    Companions.objects.create(user=user, person1=person1, person2=person2, person3=person3)

                seat_value = ""
                for seat in seat_numbers:
                    bus_id, asiento_numero = seat.split('_')
                    asiento = Asiento.objects.get(bus_id=bus_id, numero=asiento_numero)
                    if asiento.estado == 'disponible':
                        asiento.estado = 'reservado'
                        asiento.user = user
                        asiento.save()
                        seat_value += f"{asiento.bus.nombre} - Asiento {asiento.numero}, "
                    else:
                        raise ValidationError({'seat': ('Uno de los asientos seleccionados no está disponible.')})

                seat_value = seat_value.rstrip(', ')
                messages.success(request, f'Usuario registrado con éxito')
                return redirect('/')
        except ValidationError as error:
            user.delete()
            error_message = list(error.message_dict.values())[0][0]
            return render(request, 'error.html', {'message': error_message})
        
class loginView(View):
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        session = authenticate(username=username, password=password)
        if not session:
            messages.error(request, 'Inicio de sesión fallido')
            return redirect('/')
        login(request, session)
        return redirect('/')
    
def logoutView(request):
    logout(request)
    return redirect('/')

def what_price(request):
    return render(request, 'what_price.html')

def terms_and_conditions(request):
    return render(request, 'TermsAndConditions.html')