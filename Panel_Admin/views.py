from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from pageLogin.models import *
from upload_Voucher.models import *
from django.core.exceptions import ValidationError
from pagePrincipal.models import *

# Create your views here.

class panelAdminView(LoginRequiredMixin, View):
    login_url = '/'
    
    def get(self, request):
        if request.user.is_superuser:
            users = User.objects.all()
            count_users = users.count()
            buses = Bus.objects.all()
            user_with_info = []
            for user in users:
                try:
                    user_info = {
                        'user': user,
                        'moreInformation': UserMoreInformation.objects.get(user=user),
                        'totalPaid': totalPaidTable.objects.filter(user=user).last(),
                        'asientos': Asiento.objects.filter(user=user),
                        'companions': Companions.objects.get(user=user),
                        'reservations': Reservation.objects.filter(user=user),
                    }
                except UserMoreInformation.DoesNotExist:
                    user_info = {
                        'user': user,
                        'moreInformation': None, 
                        'totalPaid': None,
                        'asientos': None,
                        'companions': None,
                        'reservations': None,
                    }
                except Companions.DoesNotExist:
                    user_info = {
                        'user': user,
                        'moreInformation': UserMoreInformation.objects.get(user=user),
                        'totalPaid': totalPaidTable.objects.filter(user=user).last(),
                        'asientos': Asiento.objects.filter(user=user),
                        'companions': None,
                        'reservations': Reservation.objects.filter(user=user),
                    }
                except Reservation.DoesNotExist:
                    user_info = {
                        'user': user,
                        'moreInformation': UserMoreInformation.objects.get(user=user),
                        'totalPaid': totalPaidTable.objects.filter(user=user).last(),
                        'asientos': Asiento.objects.filter(user=user),
                        'companions': Companions.objects.get(user=user),
                        'reservations': None,
                    }
                user_with_info.append(user_info)
            return render(request, 'PanelAdmin.html', {'users': user_with_info, 'count_users': count_users, 'buses': buses})
        else:
            return redirect('/')

def deleteUser(request, user_id):
    user = User.objects.get(id=user_id)
    try:
        moreInformation = UserMoreInformation.objects.get(user=user)
        reservations = Reservation.objects.filter(user=user)
        for reservation in reservations:
            room = Room.objects.get(id=reservation.room.id)
            room.remaining_spaces = 4
            room.save()
    except UserMoreInformation.DoesNotExist:
        pass
    except Reservation.DoesNotExist:
        pass

    # Liberar los asientos reservados por el usuario
    asientos_reservados = Asiento.objects.filter(user=user)
    for asiento in asientos_reservados:
        asiento.estado = 'disponible'
        asiento.user = None
        asiento.save()
    moreInformation.delete()
    user.delete()
    return redirect('Admin')

class paymentsAdminView(LoginRequiredMixin, View):
    login_url = '/'
    
    def get(self, request, user_id):
        vouchers = uploadVoucher.objects.filter(user=user_id)
        return render(request, 'chargePayments.html', {'vouchers': vouchers})

class totalPaid(LoginRequiredMixin, View):
    login_url = '/'
    
    def get(self, request):
        return redirect('Admin')
    
    def post(self, request, user_id):
        total = request.POST['paid']
        user = User.objects.get(id=user_id)
        paid = totalPaidTable.objects.filter(user=user).last()
        if paid:
            total_paid = paid.totalPaid + float(total)
            totalPaidTable.objects.create(user=user, payments=total, totalPaid=total_paid)
        else:
            totalPaidTable.objects.create(user=user, payments=float(total), totalPaid=float(total))
        return redirect('Admin')

class viewPaymentsAdmin(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        total = totalPaidTable.objects.filter(user=user)
        return render(request, 'deletePaymentsAdmin.html', {'total': total, 'user': user})

def deletePaymentsAdmin(request, total_id, user_id):
    user = User.objects.get(id=user_id)
    total = totalPaidTable.objects.get(id=total_id)
    total.delete()
    
    # Obtener todos los registros de totalPaidTable asociados al usuario
    total_paid_records = totalPaidTable.objects.filter(user=user)
    
    # Calcular la suma total de los pagos
    total_payments_sum = total_paid_records.aggregate(Sum('payments'))['payments__sum']
    
    if total_payments_sum is None:
        total_payments_sum = 0
    
    # Obtener la instancia más reciente de totalPaidTable
    total_paid = total_paid_records.last()
    
    # Actualizar el campo totalPaid con la suma total de los pagos
    if total_paid:
        total_paid.totalPaid = total_payments_sum
        total_paid.save()
    return redirect(f'/view_payments_admin/{user_id}/')

class viewBus(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request, bus_id):
        bus = Bus.objects.get(id=bus_id)
        seats = Asiento.objects.filter(bus=bus)
        users = User.objects.all()
        return render(request, 'viewBus.html', {'seats': seats, 'bus': bus, 'users': users})
    
class makeAvailable(LoginRequiredMixin, View):
    login_url = '/'
    def post(self, request, asiento_id):
        asiento = Asiento.objects.get(id=asiento_id)
        asiento.user = None
        asiento.estado = 'disponible'
        asiento.save()
        return redirect('ViewBus', bus_id=asiento.bus.id)
    
class defineSeat(LoginRequiredMixin, View):
    login_url = '/'
    def post(self, request, seat_id):
        asiento = Asiento.objects.get(id=seat_id)
        user = request.POST['user']
        try:
            try:
                user_search = User.objects.get(id=user)
                asiento.user = user_search
                asiento.estado = 'reservado'
                asiento.save()
                return redirect('ViewBus', bus_id=asiento.bus.id)
            except ValidationError as error:
                error_message = list(error.message_dict.values())[0][0]
                button = 'Back to Panel Admin'
                redirectURL = '/admin666/'
                return render(request, 'error.html', {'message': error_message, 'button': button, 'redirect': redirectURL})
        except User.DoesNotExist:
            messages.error(request, 'User not found')
            return redirect('ViewBus', bus_id=asiento.bus.id)
        
class addSeats(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request, bus_id):
        return render(request, 'addSeats.html', {'bus': Bus.objects.get(id=bus_id)})
    def post(self, request, bus_id):
        bus = Bus.objects.get(id=bus_id)
        seat = request.POST.get('seat')
        seats, created = Asiento.objects.get_or_create(bus=bus, numero=seat)
        if not created:
            messages.error(request, 'Seat right created')
            return redirect('ViewBus', bus_id)
        else:
            seats.estado = 'disponible'
            seats.save()
            return redirect('ViewBus', bus_id)

class viewRooms(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        rooms = Room.objects.all()
        return render(request, 'view-rooms.html', {'rooms': rooms})
    
class addRooms(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        return render(request, 'addRoom.html')
    def post(self, request):
        room = request.POST.get('room')
        Room.objects.create(number=room)
        messages.success(request, 'Habitación agregada correctamente')
        return redirect('ViewRooms')
    
class modifyUser(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        rooms = Room.objects.all()
        buses = Bus.objects.all()
        asientos_disponibles = {bus.nombre: Asiento.objects.filter(bus=bus) for bus in buses}
        fechas = DatesOfTravel.objects.all()
        try:
            moreInformation = UserMoreInformation.objects.get(user=user)
        except UserMoreInformation.DoesNotExist:
            moreInformation = None
        try:
            reservation = Reservation.objects.filter(user=user)
            reservation = reservation.first()
        except Reservation.DoesNotExist:
            reservation = None
        try:
            companions = Companions.objects.get(user=user)
        except Companions.DoesNotExist:
            companions = None
        return render(request, 'modifyUser.html', {'user': user, 'rooms': rooms, 'asientos': asientos_disponibles, 'dates': fechas, 'reservation': reservation, 'moreInformation': moreInformation, 'companions': companions})
    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        if user.is_superuser:
            user.username = request.POST.get('username')
            user.first_name = request.POST.get('name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            return redirect('Admin')
        people = int(request.POST.get('people'))
        number_room = request.POST.get('number_room')
        rooms = request.POST.getlist('rooms')
        if people == "Seleccionar...":
            messages.error(request, 'Debe seleccionar la cantidad de personas')
            return redirect('/modify_user/' + str(user_id))
        if number_room == "Seleccionar...":
            messages.error(request, 'Debe seleccionar la habitación')
            return redirect('/modify_user/' + str(user_id))
        if rooms == "Seleccionar...":
            messages.error(request, 'Debe seleccionar la cantidad de habitaciones')
            return redirect('/modify_user/' + str(user_id))
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        moreInfo = UserMoreInformation.objects.get(user=user)
        radioVip = request.POST.get('RadioVip')
        person1 = request.POST.get('person1')
        person2 = request.POST.get('person2')
        person3 = request.POST.get('person3')
        moreInfo.people = people
        moreInfo.rooms = request.POST.get('rooms')

        dates = request.POST.get('dates')
        # Convierte dates a entero si es necesario
        dates = int(dates)
        try:
            date = DatesOfTravel.objects.get(id=dates)
            moreInfo.date_of_travel = date
        except DatesOfTravel.DoesNotExist:
            messages.error(request, 'Seleccione la fecha')
            return redirect('/modify_user/' + str(user_id))
        vip = False
        for data in range(1, 5):
            if people == data:
                if radioVip == "Yes":
                    price =  Prices.objects.get(people=4).total
                    vip = True
                    break
                else:
                    if data == 1:
                        price = Prices.objects.get(people=4).price
                        price = price
                        vip = False
                    else:
                        price = Prices.objects.get(people=data).total
                        vip = False
        moreInfo.price = price
        try:
            compa = Companions.objects.get(user=user)
            if people == 1:
                compa.delete()
            elif people == 2:
                compa.person1 = person1
                compa.person2 = ""
                compa.person3 = ""
                compa.save()
            elif people == 3:
                compa.person1 = person1
                compa.person2 = person2
                compa.person3 = ""
                compa.save()
            else:
                compa.person1 = person1
                compa.person2 = person2
                compa.person3 = person3
                compa.save()
            for data in range(1, 5):
                if people == data:
                    reservation = Reservation.objects.get(user=user)
                    if compa.person1 != '':
                        data = data - 1
                    elif compa.person2 != '':
                        data = data - 2
                    elif compa.person3 != '':
                        data = data - 3
                    if reservation.number_of_people > people:
                        if reservation.number_of_people == 2:
                            person = 1
                        elif reservation.number_of_people == 3:
                            if people == 2:
                                person = 1
                            else:
                                person = 2
                        elif reservation.number_of_people == 4:
                            if people == 3:
                                person = 2
                            else:
                                person = 3
                        room_id = Room.objects.get(id=number_room)
                        spaces = room_id.remaining_spaces + person
                        reservation.start_date = date.first_date
                        reservation.end_date = date.second_date
                        reservation.number_of_people = people
                        reservation.exclusive = vip
                        reservation.save()
                        room_id.remaining_spaces = spaces
                        room_id.save()
                    else:
                        room_id = Room.objects.get(id=number_room)
                        spaces = room_id.remaining_spaces - data
                        reservation.start_date = date.first_date
                        reservation.end_date = date.second_date
                        reservation.number_of_people = people
                        reservation.exclusive = vip
                        reservation.save()
                        room_id.remaining_spaces = spaces
                        room_id.save()
        except Companions.DoesNotExist:
            for data in range(1, 5):
                if people == data:
                    reservation = Reservation.objects.get(user=user)
                    if reservation.number_of_people == people:
                        break
                    if reservation.number_of_people > data:
                        Companions.objects.create(user=user, person1=person1, person2=person2, person3=person3)
                        room_id = Room.objects.get(id=number_room)
                        spaces = room_id.remaining_spaces + data
                        print(f'{room_id.remaining_spaces} - {data}')
                        reservation.start_date = date.first_date
                        reservation.end_date = date.second_date
                        reservation.number_of_people = people
                        reservation.exclusive = vip
                        reservation.save()
                        room_id.remaining_spaces = spaces
                        room_id.save()
                    else:
                        Companions.objects.create(user=user, person1=person1, person2=person2, person3=person3)
                        room_id = Room.objects.get(id=number_room)
                        data = data - 1
                        spaces = room_id.remaining_spaces - data
                        reservation.start_date = date.first_date
                        reservation.end_date = date.second_date
                        reservation.number_of_people = people
                        reservation.exclusive = vip
                        reservation.save()
                        room_id.remaining_spaces = spaces
                        room_id.save()
        moreInfo.save()
        # Obtener los números de asiento seleccionados del formulario
        seat_numbers = request.POST.getlist('seat_numbers')
        # Verificar si se han seleccionado asientos nuevos
        if seat_numbers:
            # Buscar los asientos previamente seleccionados por el usuario y liberarlos
            asientos_ocupados = Asiento.objects.filter(user=user)
            for asiento_ocupado in asientos_ocupados:
                asiento_ocupado.user = None
                asiento_ocupado.estado = 'disponible'
                asiento_ocupado.save()

                # Inicializar la variable para almacenar los nuevos asientos asignados
            seat_value = ""

            # Asignar los nuevos asientos seleccionados al usuario
            for seat in seat_numbers:
                bus_id, asiento_numero = seat.split('_')
                asiento = Asiento.objects.get(bus_id=bus_id, numero=asiento_numero)

                # Verificar si el asiento está disponible antes de asignarlo
                try:
                    if asiento.estado == 'disponible':
                        asiento.estado = 'reservado'
                        asiento.user = user
                        asiento.save()
                        seat_value += f"{asiento.bus.nombre} - Seat {asiento.numero}, "
                    else:
                        messages.error(request, 'Uno de los asientos seleccionados no está disponible')
                        return redirect('/modify_user/' + str(user_id))
                except ValidationError as error:
                    error_message = list(error.message_dict.values())[0][0]
                    button = 'Volver a modificar el usuario'
                    return render(request, 'error.html', {'message': error_message, 'button': button})

                # Eliminar la última coma y espacio de la cadena seat_value
            seat_value = seat_value.rstrip(', ')

        # Si no se seleccionaron nuevos asientos, no hacer nada adicional
        else:
            # Puedes agregar algún manejo adicional si es necesario
            pass
        messages.success(request, 'Usuario modificado correctamente')
        return redirect('Admin')
    
class modifyPrices(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        prices = Prices.objects.all()
        return render(request, 'modifyPrices.html', {'prices': prices})
    def post(self, request):
        price1 = request.POST.get('price1')
        price2 = request.POST.get('price2')
        price3 = request.POST.get('price3')
        price4 = request.POST.get('price4')
        prices = Prices.objects.all()
        for price in prices:
            if price.people == 1:
                if price1 == '':
                    pass
                elif price1.isspace():
                    pass
                else:
                    price.price = float(price1)
            elif price.people == 2:
                if price2 == '':
                    pass
                elif price2.isspace():
                    pass
                else:
                    price.price = float(price2)
            elif price.people == 3:
                if price3 == '':
                    pass
                elif price3.isspace():
                    pass
                else:
                    price.price = float(price3)
            elif price.people == 4:
                if price4 == '':
                    pass
                elif price4.isspace():
                    pass
                else:
                    price.price = float(price4)
            price.save()
        messages.success(request, 'Precios modificados correctamente')
        return redirect('Admin')
    
class modifyDates(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        dates = DatesOfTravel.objects.all()
        return render(request, 'modifyDates.html', {'dates': dates})
    def post(self, request):
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        change = request.POST.get('change')
        try:
            dateChange = DatesOfTravel.objects.get(id=change)
            dateChange.first_date = start_date
            dateChange.second_date = end_date
            dateChange.save()
            messages.success(request, 'Fecha de viaje modificada correctamente')
            return redirect('Admin')
        except ValidationError as error:
            error_message = list(error.message_dict.values())[0][0]
            button = 'Volver a modificar las fechas'
            return render(request, 'error.html', {'message': error_message, 'button': button})
        

class createAdmin(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        return render(request, 'createAdmin.html')
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        try:
            User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email, is_superuser=True)
            messages.success(request, 'Usuario creado correctamente')
            return redirect('Admin')
        except ValidationError as error:
            error_message = list(error.message_dict.values())[0][0]
            button = 'Volver a crear el usuario'
            return render(request, 'error.html', {'message': error_message, 'button': button})