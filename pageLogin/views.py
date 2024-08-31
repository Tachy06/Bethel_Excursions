from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth import login, logout, authenticate
from django.db import transaction
from pagePrincipal.models import *
from upload_Voucher.models import *
from Panel_Admin.models import *
import json

class RegisterView(View):
    def get(self, request):
        buses = Bus.objects.all()
        asientos_disponibles = {bus.nombre: Asiento.objects.filter(bus=bus).order_by('numero') for bus in buses}
        fechas = DatesOfTravel.objects.all()
        prices_1 = Prices.objects.get(people=1).total
        prices_2 = Prices.objects.get(people=2).total
        prices_3 = Prices.objects.get(people=3).total
        prices_4 = Prices.objects.get(people=4).total
        price_normal = Prices.objects.get(people=4).price
        prices = Prices.objects.get(people=4)
        return render(request, 'register.html', {
            'asientos': asientos_disponibles,
            'dates': fechas,
            'price': prices,
            'prices_1': prices_1,
            'prices_2': prices_2,
            'prices_3': prices_3,
            'prices_4': prices_4,
            'price_normal': price_normal,
        })

    def post(self, request):
        first_name = request.POST['first_name']
        first_last_name = request.POST['first_last_name']
        second_last_name = request.POST['second_last_name']
        last_name = f"{first_last_name} {second_last_name}"
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        people = int(request.POST['people'])
        seat_numbers = request.POST.getlist('seat_numbers')
        dates = request.POST['dates']
        radioVip = request.POST.get('RadioVip')
        person1_name = request.POST.get('person1')
        person2_name = request.POST.get('person2')
        person3_name = request.POST.get('person3')

        if not seat_numbers:
            messages.error(request, 'Selecciona un asiento disponible')
            return redirect('/register/')

        if len(seat_numbers) > people:
            message = f"El usuario {username} no puede reservar más de {people} asiento(s)"
            button = "Redirigir a Registrar"
            redirectURL = '/register/'
            return render(request, 'error.html', {'message': message, 'button': button, 'redirect': redirectURL})
        elif len(seat_numbers) < people:
            message = f"El usuario {username} no puede reservar menos de {people} asiento(s)"
            button = "Redirigir a Registrar"
            redirectURL = '/register/'
            return render(request, 'error.html', {'message': message, 'button': button, 'redirect': redirectURL})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuario ya registrado')
            return redirect('/register/')

        with transaction.atomic():
            # Determinar precio y exclusividad
            if people > 1:
                if radioVip == "Yes":
                    vip = True
                    price = Prices.objects.get(people=people).total
                else:
                    vip = False
                    price = Prices.objects.get(people=4).price
                    price = price * people
            else:
                if people == 1:
                    if radioVip == "Yes":
                        vip = True
                        price = Prices.objects.get(people=1).total
                    else:
                        vip = False
                        price = Prices.objects.get(people=4).price

            # Crear el usuario
            user_create = User.objects.create(first_name=first_name, last_name=last_name, username=username, email=email)
            user_create.set_password(password)
            user_create.save()

            # Obtener la fecha del viaje
            fechas = DatesOfTravel.objects.get(id=dates)

            # Crear los acompañantes
            companions = None
            if people > 1:
                companions = []
                if person1_name:
                    companions.append(Companions.objects.create(user=user_create, name=person1_name))
                if person2_name:
                    companions.append(Companions.objects.create(user=user_create, name=person2_name))
                if person3_name:
                    companions.append(Companions.objects.create(user=user_create, name=person3_name))

            # Asignar asientos
            first_seat = seat_numbers.pop(0)  # Obtener el primer asiento para el usuario principal
            bus_id, asiento_numero = first_seat.split('_')
            bus = Bus.objects.get(id=bus_id)
            asiento = Asiento.objects.get(bus_id=bus_id, numero=asiento_numero)
            if asiento.estado == 'disponible':
                asiento.estado = 'reservado'
                asiento.user = user_create
                asiento.save()
                seat_value = f"{asiento.bus.nombre} - Asiento {asiento.numero} (Asignado al usuario), "
            else:
                raise ValidationError('Uno de los asientos seleccionados no está disponible.')

            # Asignar los asientos restantes a los acompañantes
            if companions:
                for seat, companion in zip(seat_numbers, companions):
                    bus_id, asiento_numero = seat.split('_')
                    try:
                        asiento = Asiento.objects.get(bus_id=bus_id, numero=asiento_numero, estado='disponible')
                        companion_search = Companions.objects.filter(user=user_create, id=companion.id).first()
                        
                        if companion_search:
                            asiento.estado = 'reservado'
                            asiento.user = user_create
                            asiento.companion = companion_search
                            asiento.companion_name = companion_search.name
                            asiento.save()
                            seat_value += f"{asiento.bus.nombre} - Asiento {asiento.numero} (Asignado a {companion_search.name}), "
                        else:
                            raise ValidationError(f'No se encontró el compañero con ID {companion.id} para el usuario {user_create}.')
                            
                    except Asiento.DoesNotExist:
                        raise ValidationError(f'El asiento {asiento_numero} en el bus {bus_id} no está disponible o no existe.')


            moreInfo = UserMoreInformation.objects.create(user=user_create, people=people, price=price, date_of_travel=fechas, bus=bus, vip=vip)

            # Subir el comprobante de pago
            upload = uploadVoucher.objects.create(user=user_create)
            if 'voucher' in request.FILES:
                voucher = request.FILES['voucher']
                binary_data = voucher.read()
                upload.voucher = binary_data
                upload.save()

            # Registrar el pago total
            total_payment = {1: 500, 2: 1000, 3: 1500, 4: 2000}
            if people in total_payment:
                totalPaidTable.objects.create(user=user_create, payments=total_payment[people], totalPaid=total_payment[people], date=fechas)

            messages.success(request, 'Usuario registrado con éxito')
            return redirect('/')
        
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