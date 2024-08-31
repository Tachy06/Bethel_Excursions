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
import base64
from django.db.models import IntegerField
from django.db.models.functions import Cast


# Create your views here.

class panelAdminView(LoginRequiredMixin, View):
    login_url = '/'
    
    def get(self, request):
        if request.user.is_superuser:
            users = User.objects.all()
            count_users = users.count()
            buses = Bus.objects.all()
            user_with_info = []
            room = None
            room_companion = None
            for user in users:
                total_paid = 0
                paid = 0
                try:
                    more_information = UserMoreInformation.objects.get(user=user)
                    paid = totalPaidTable.objects.filter(user=user).last()
                    total_paid = float(more_information.price) - float(paid.totalPaid)
                    room = Room.objects.get(users=user)
                except UserMoreInformation.DoesNotExist:
                    more_information = None
                except Room.DoesNotExist:
                    room = None
                
                # Obtener los asientos asignados y los acompañantes
                asientos = Asiento.objects.filter(user=user)
                seat_numbers = [asiento for asiento in asientos] if asientos else []

                companion_rooms = []
                try:
                    companions = Companions.objects.filter(user=user)
                    for companion in companions:
                        try:
                            room = Room.objects.get(companions=companion)
                        except Room.DoesNotExist:
                            room = None
                        companion_rooms.append((companion, room))
                except Companions.DoesNotExist:
                    companion_rooms = []

                user_info = {
                    'user': user,
                    'moreInformation': more_information,
                    'debe': total_paid,
                    'totalPaid': totalPaidTable.objects.filter(user=user).last(),
                    'reservations': Reservation.objects.filter(user=user),
                    'seat': seat_numbers,
                    'companions': companions,
                    'room_companion': room_companion,
                    'room': room
                }
                user_with_info.append(user_info)

            return render(request, 'PanelAdmin.html', {'users': user_with_info, 'companion_rooms': companion_rooms, 'count_users': count_users, 'buses': buses})
        else:
            return redirect('/')
    def post(self, request):
        username = request.POST['username']
        try:
            user = User.objects.get(username=username)
            moreInfo = UserMoreInformation.objects.get(user=user)
            asientos = Asiento.objects.filter(user=user)
            companions = Companions.objects.filter(user=user)
            totalPaid = totalPaidTable.objects.filter(user=user).last()
            debe = float(moreInfo.price) - float(totalPaid.totalPaid)
        except User.DoesNotExist:
            messages.error(request, 'El usuario no existe')
            return redirect('Admin')
        except UserMoreInformation.DoesNotExist:
            user = User.objects.get(username=username)
            moreInfo = None
            asientos = None
            companions = None
            totalPaid = None
            debe = None
            return render(request, 'UserSearch.html', {'user': user, 'moreInfo': moreInfo, 'asientos': asientos, 'companions': companions, 'totalPaid': totalPaid, 'debe': debe})
        return render(request, 'UserSearch.html', {'user': user, 'moreInfo': moreInfo, 'asientos': asientos, 'companions': companions, 'totalPaid': totalPaid, 'debe': debe})

def deleteUser(request, user_id):
    user = User.objects.get(id=user_id)
    companions = None
    try:
        moreInformation = UserMoreInformation.objects.get(user=user)
    except UserMoreInformation.DoesNotExist:
        pass

    # Liberar los asientos reservados por el usuario
    asientos_reservados = Asiento.objects.filter(user=user)
    for asiento in asientos_reservados:
        asiento.estado = 'disponible'
        asiento.user = None
        asiento.companion = None
        asiento.companion_name = None
        asiento.save()

    rooms_reserved = Room.objects.filter(users=user)
    for room in rooms_reserved:
        room.users.remove(user)
        room.remaining_spaces += 1
        room.save()
    try:
        companions = Companions.objects.filter(user=user)
        for companion in companions:
            rooms_reserved_companion = Room.objects.filter(companions=companion)
            for room in rooms_reserved_companion:
                room.companions.remove(companion)
                room.remaining_spaces += 1
                room.save()
                companion.delete()
    except Companions.DoesNotExist:
        pass
    moreInformation.delete()
    user.delete()
    return redirect('Admin')

class paymentsAdminView(LoginRequiredMixin, View):
    login_url = '/'
    
    def get(self, request, user_id):
        vouchers = uploadVoucher.objects.filter(user=user_id)
        voucher_files = []
        for voucher in vouchers:
            base64_data = base64.b64encode(voucher.voucher).decode('utf-8')
            voucher_files.append({
                'id': voucher.id,
                'base64_data': base64_data,
                'date': voucher.date
            })
        return render(request, 'chargePayments.html', {'vouchers': voucher_files})

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

def deleteVoucher(request, voucher_id):
    voucher = uploadVoucher.objects.get(id=voucher_id)
    voucher.delete()
    return redirect('Admin')

class viewBus(LoginRequiredMixin, View):
    login_url = '/'
    
    def get(self, request, bus_id):
        bus = Bus.objects.get(id=bus_id)
        seats = Asiento.objects.filter(bus=bus).order_by('numero')
        
        # Obtener los usuarios y compañeros asociados con el bus
        more_info = UserMoreInformation.objects.filter(bus=bus)
        users = User.objects.filter(id__in=more_info.values('user_id'))
        companions = Companions.objects.filter(user__in=users)
        
        # Obtener IDs de los usuarios y compañeros que ya tienen un asiento reservado
        reserved_users_ids = Asiento.objects.filter(bus=bus, user__isnull=False).values_list('user_id', flat=True).distinct()
        reserved_companion_ids = Asiento.objects.filter(bus=bus, companion__isnull=False).values_list('companion_id', flat=True).distinct()
        
        # Filtrar usuarios que no tienen un asiento reservado
        available_users = users.exclude(id__in=reserved_users_ids)
        
        # Filtrar compañeros que no tienen un asiento reservado
        available_companions = companions.exclude(id__in=reserved_companion_ids)
        
        return render(request, 'viewBus.html', {
            'seats': seats,
            'bus': bus,
            'users': available_users,
            'companions': available_companions
        })
    
class DeleteRoom(LoginRequiredMixin, View):
    login_url = '/'
    def post(self, request, bus_id, room_id):
        room = Room.objects.get(id=room_id)
        room.delete()
        messages.success(request, 'Habitación eliminada correctamente')
        return redirect('ViewRooms', bus_id)
        
def deleteSeat(request, asiento_id, bus_id):
    asiento = Asiento.objects.get(id=asiento_id)
    asiento.delete()
    return redirect('ViewBus', bus_id)

class makeAvailable(LoginRequiredMixin, View):
    login_url = '/'
    def post(self, request, asiento_id):
        asiento = Asiento.objects.get(id=asiento_id)
        asiento.user = None
        asiento.companion = None
        asiento.companion_name = None
        asiento.estado = 'disponible'
        asiento.save()
        return redirect('ViewBus', bus_id=asiento.bus.id)
    
class defineSeat(LoginRequiredMixin, View):
    login_url = '/'
    
    def post(self, request, seat_id):
        asiento = Asiento.objects.get(id=seat_id)
        user_selection = request.POST['user']
        user_info, user_type = user_selection.split('|')
        user_search = None

        try:
            if user_type == 'main':
                user_search = User.objects.get(username=user_info)
                # Check if the user has already reserved a seat in this bus
                existing_seat_user = Asiento.objects.filter(bus=asiento.bus, user=user_search).exists()
                if existing_seat_user:
                    messages.error(request, 'Este usuario ya reservó un asiento en este bus.')
                    return redirect('ViewBus', bus_id=asiento.bus.id)
                asiento.user = user_search
                asiento.estado = 'reservado'
                asiento.companion = None
                asiento.companion_name = None
                asiento.save()
            else:
                # Handle companions
                companions_search = Companions.objects.filter(id=user_info)
                companion_name = ''
                for companion in companions_search:
                    companion_name = companion.name
                existing_seat = Asiento.objects.filter(bus=asiento.bus, companion_name=companion_name).exists()
                
                if existing_seat:
                    messages.error(request, 'Esta persona ya reservó un asiento en este bus.')
                    return redirect('ViewBus', bus_id=asiento.bus.id)
                else:
                    for companion in companions_search:
                        asiento.companion_name = companion_name
                        asiento.companion = companion
                        asiento.user = companion.user
                        asiento.estado = 'reservado'
                        asiento.save()
            
            return redirect('ViewBus', bus_id=asiento.bus.id)

        except User.DoesNotExist:
            error_message = "Usuario no encontrado."
            button = 'Back to Panel Admin'
            redirectURL = '/admin/'
            return render(request, 'error.html', {'message': error_message, 'button': button, 'redirect': redirectURL})
        
        except Companions.DoesNotExist:
            error_message = "Compañero no encontrado."
            button = 'Back to Panel Admin'
            redirectURL = '/admin/'
            return render(request, 'error.html', {'message': error_message, 'button': button, 'redirect': redirectURL})
        
class addSeats(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request, bus_id):
        return render(request, 'addSeats.html', {'bus': Bus.objects.get(id=bus_id)})
    def post(self, request, bus_id):
        bus = Bus.objects.get(id=bus_id)
        seat = request.POST.get('seat')
        seats, created = Asiento.objects.get_or_create(bus=bus, numero=seat)
        if not created:
            messages.error(request, 'Asiento creado')
            return redirect('ViewBus', bus_id)
        else:
            seats.estado = 'disponible'
            seats.save()
            bus_id2 = bus_id + 1
            return redirect('ViewBus', bus_id)
        
class viewRooms(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request, room_id):
        room = Rooms_Bus.objects.get(bus=room_id)
        rooms = Room.objects.annotate(
            number_as_int=Cast('number', IntegerField())
        ).filter(rooms_bus=room).order_by('number_as_int')
        bus_id = room_id
        return render(request, 'view-rooms.html', {'rooms': rooms, 'room_search': room, 'bus_id': bus_id})
    
class addRooms(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, bus_id):
        room_bus = Rooms_Bus.objects.get(bus=bus_id)
        return render(request, 'addRoom.html', {'room_bus': room_bus, 'bus_id': bus_id})

    def post(self, request, bus_id):
        room_number = request.POST.get('room')
        room_bus = Rooms_Bus.objects.get(bus=bus_id)
        Room.objects.create(number=room_number, rooms_bus=room_bus)
        messages.success(request, 'Habitación agregada correctamente')
        return redirect('ViewRooms', bus_id)
    

class addUserToRoom(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, room_id, bus_id):
        # Obtener el objeto Bus
        try:
            bus = Bus.objects.get(id=bus_id)
        except Bus.DoesNotExist:
            messages.error(request, 'Bus no encontrado.')
            return redirect('ViewRooms', room_id)
        
        # Filtrar UserMoreInformation por el bus específico
        users_info = UserMoreInformation.objects.filter(bus=bus)
        
        # Obtener los usuarios asociados al bus
        users_dict = [user_info.user for user_info in users_info]

        # Obtener la habitación específica
        room = Room.objects.get(id=room_id)

        # Obtener usuarios asignados a la habitación específica
        assigned_users = room.users.all()

        # Obtener acompañantes asignados a la habitación específica
        assigned_companions = room.companions.all()

        # Filtrar usuarios disponibles (sin habitación asignada)
        available_users = [user for user in users_dict if user not in assigned_users]
        
        # Filtrar compañeros disponibles (sin habitación asignada)
        # Obtener todos los acompañantes asociados a los usuarios disponibles
        companions = Companions.objects.all()
        all_available_companions = [companion for companion in companions if companion not in assigned_companions]
        
        # Filtrar compañeros disponibles (que no estén ya asignados a la habitación)

        return render(request, 'addUserToRoom.html', {
            'users': available_users, 
            'companions': all_available_companions,
            'room_id': room_id, 
            'bus_id': bus_id 
        })


    def post(self, request, room_id, bus_id):
        user1 = request.POST.get('user1')
        user2 = request.POST.get('user2')
        user3 = request.POST.get('user3')
        user4 = request.POST.get('user4')

        room = Room.objects.get(id=room_id)

        user_1 = None
        user_2 = None
        user_3 = None
        user_4 = None

        user_type1 = None
        user_type2 = None
        user_type3 = None
        user_type4 = None

        spaces = 0

        if room.remaining_spaces == 0:
            messages.error(request, 'No hay campo disponible en esta habitación')
            return redirect('ViewRooms', bus_id)

        if user1 != '0':
            user_1, user_type1 = user1.split('|')
        if user2 != '0':
            user_2, user_type2 = user2.split('|')
        if user3 != '0':
            user_3, user_type3 = user3.split('|')
        if user4 != '0':
            user_4, user_type4 = user4.split('|')

        if user_type1 == 'user':
            try:
                room_reserved = Room.objects.get(users=User.objects.get(username=user_1))
                if room_reserved:
                    messages.error(request, 'El usuario ya se encuentra en una habitación reservada')
                    return redirect('ViewRooms', bus_id)
            except Room.DoesNotExist:
                user_search = User.objects.get(username=user_1)
                moreInfo = UserMoreInformation.objects.get(user=user_search)
                if moreInfo.vip:
                    if room.users.exists():
                        messages.error(request, 'Esta habitación ya tiene usuarios, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    elif room.companions.exists():
                        messages.error(request, 'Esta habitación ya tiene acompañantes, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    else:
                        room.users.add(user_search)
                        companions = Companions.objects.filter(user=user_search)
                        for companion in companions:
                            room.companions.add(companion)
                        spaces = room.remaining_spaces - 4
                        room.remaining_spaces = spaces
                        room.save()
                        messages.success(request, 'Habitación reservada correctamente')
                        return redirect('ViewRooms', bus_id)
                else:
                    room.users.add(user_search)
                    spaces = room.remaining_spaces - 1
                    room.remaining_spaces = spaces
                    room.save()
        elif user_type1 == 'companion':
            try:
                room_reserved = Room.objects.get(companions=Companions.objects.get(id=user_1))
                if room_reserved:
                    messages.error(request, 'La persona ya se encuentra en una habitación reservada')
                    return redirect('ViewRooms', bus_id)
            except Room.DoesNotExist:
                companion_search = Companions.objects.get(id=user_1)
                moreInfo = UserMoreInformation.objects.get(user=companion_search.user)
                if moreInfo.vip:
                    if room.users.exists():
                        messages.error(request, 'Esta habitación ya tiene usuarios, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    elif room.companions.exists():
                        messages.error(request, 'Esta habitación ya tiene acompañantes, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    else:
                        room.companions.add(companion_search)
                        user = User.objects.get(username=companion_search.user.username)
                        companions = Companions.objects.filter(user=user)
                        for companion in companions:
                            if companion.id == companion_search.id:
                                pass
                            else:
                                room.companions.add(companion)
                        room.users.add(user)
                        spaces = room.remaining_spaces - 4
                        room.remaining_spaces = spaces
                        room.save()
                        messages.success(request, 'Habitación reservada correctamente')
                        return redirect('ViewRooms', bus_id)
                else:
                    room.companions.add(companion_search)
                    spaces = room.remaining_spaces - 1
                    room.remaining_spaces = spaces
                    room.save()

        if user_type2 == 'user':
            try:
                room_reserved = Room.objects.get(users=User.objects.get(username=user_2))
                if room_reserved:
                    messages.error(request, 'El usuario ya se encuentra en una habitación reservada')
                    return redirect('ViewRooms', bus_id)
            except Room.DoesNotExist:
                user_search = User.objects.get(username=user_2)
                moreInfo = UserMoreInformation.objects.get(user=user_search)
                if moreInfo.vip:
                    if room.users.exists():
                        messages.error(request, 'Esta habitación ya tiene usuarios, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    elif room.companions.exists():
                        messages.error(request, 'Esta habitación ya tiene acompañantes, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    else:
                        room.users.add(user_search)
                        companions = Companions.objects.filter(user=user_search)
                        for companion in companions:
                            room.companions.add(companion)
                        spaces = room.remaining_spaces - 4
                        room.remaining_spaces = spaces
                        room.save()
                        messages.success(request, 'Habitación reservada correctamente')
                        return redirect('ViewRooms', bus_id)
                else:
                    room.users.add(user_search)
                    spaces = room.remaining_spaces - 1
                    room.remaining_spaces = spaces
                    room.save()

        elif user_type2 == 'companion':
            try:
                room_reserved = Room.objects.get(companions=Companions.objects.get(id=user_2))
                if room_reserved:
                    messages.error(request, 'La persona ya se encuentra en una habitación reservada')
                    return redirect('ViewRooms', bus_id)
            except Room.DoesNotExist:
                companion_search = Companions.objects.get(id=user_2)
                moreInfo = UserMoreInformation.objects.get(user=companion_search.user)
                if moreInfo.vip:
                    if room.users.exists():
                        messages.error(request, 'Esta habitación ya tiene usuarios, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    elif room.companions.exists():
                        messages.error(request, 'Esta habitación ya tiene acompañantes, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    else:
                        room.companions.add(companion_search)
                        user = User.objects.get(username=companion_search.user.username)
                        companions = Companions.objects.filter(user=user)
                        for companion in companions:
                            if companion.id == companion_search.id:
                                pass
                            else:
                                room.companions.add(companion)
                        spaces = room.remaining_spaces - 4
                        room.remaining_spaces = spaces
                        room.save()
                        messages.success(request, 'Habitación reservada correctamente')
                        return redirect('ViewRooms', bus_id)
                else:
                    room.companions.add(companion_search)
                    spaces = room.remaining_spaces - 1
                    room.remaining_spaces = spaces
                    room.save()

        if user_type3 == 'user':
            try:
                room_reserved = Room.objects.get(users=User.objects.get(username=user_3))
                if room_reserved:
                    messages.error(request, 'El usuario ya se encuentra en una habitación reservada')
                    return redirect('ViewRooms', bus_id)
            except Room.DoesNotExist:
                user_search = User.objects.get(username=user_3)
                moreInfo = UserMoreInformation.objects.get(user=user_search)
                if moreInfo.vip:
                    if room.users.exists():
                        messages.error(request, 'Esta habitación ya tiene usuarios, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    elif room.companions.exists():
                        messages.error(request, 'Esta habitación ya tiene acompañantes, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    else:
                        room.users.add(user_search)
                        companions = Companions.objects.filter(user=user_search)
                        for companion in companions:
                            room.companions.add(companion)
                        spaces = room.remaining_spaces - 4
                        room.remaining_spaces = spaces
                        room.save()
                        messages.success(request, 'Habitación reservada correctamente')
                        return redirect('ViewRooms', bus_id)
                else:
                    room.users.add(user_search)
                    spaces = room.remaining_spaces - 1
                    room.remaining_spaces = spaces
                    room.save()

        elif user_type3 == 'companion':
            try:
                room_reserved = Room.objects.get(companions=Companions.objects.get(id=user_3))
                if room_reserved:
                    messages.error(request, 'La persona ya se encuentra en una habitación reservada')
                    return redirect('ViewRooms', bus_id)
            except Room.DoesNotExist:
                companion_search = Companions.objects.get(id=user_3)
                moreInfo = UserMoreInformation.objects.get(user=companion_search.user)
                if moreInfo.vip:
                    if room.users.exists():
                        messages.error(request, 'Esta habitación ya tiene usuarios, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    elif room.companions.exists():
                        messages.error(request, 'Esta habitación ya tiene acompañantes, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    else:
                        room.companions.add(companion_search)
                        user = User.objects.get(username=companion_search.user.username)
                        companions = Companions.objects.filter(user=user)
                        for companion in companions:
                            if companion.id == companion_search.id:
                                pass
                            else:
                                room.companions.add(companion)
                        room.users.add(user)
                        spaces = room.remaining_spaces - 4
                        room.remaining_spaces = spaces
                        room.save()
                else:
                    room.companions.add(companion_search)
                    spaces = room.remaining_spaces - 1
                    room.remaining_spaces = spaces
                    room.save()

        if user_type4 == 'user':
            try:
                room_reserved = Room.objects.get(users=User.objects.get(username=user_4))
                if room_reserved:
                    messages.error(request, 'El usuario ya se encuentra en una habitación reservada')
                    return redirect('ViewRooms', bus_id)
            except Room.DoesNotExist:
                user_search = User.objects.get(username=user_4)
                moreInfo = UserMoreInformation.objects.get(user=user_search)
                if moreInfo.vip:
                    if room.users.exists():
                        messages.error(request, 'Esta habitación ya tiene usuarios, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    elif room.companions.exists():
                        messages.error(request, 'Esta habitación ya tiene acompañantes, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    else:
                        room.users.add(user_search)
                        companions = Companions.objects.filter(user=user_search)
                        for companion in companions:
                            room.companions.add(companion)
                        spaces = room.remaining_spaces - 4
                        room.remaining_spaces = spaces
                        room.save()
                        messages.success(request, 'Habitación reservada correctamente')
                        return redirect('ViewRooms', bus_id)
                else:
                    room.users.add(user_search)
                    spaces = room.remaining_spaces - 1
                    room.remaining_spaces = spaces
                    room.save()
        elif user_type4 == 'companion':
            try:
                room_reserved = Room.objects.get(companions=Companions.objects.get(id=user_4))
                if room_reserved:
                    messages.error(request, 'La persona ya se encuentra en una habitación reservada')
                    return redirect('ViewRooms', bus_id)
            except Room.DoesNotExist:
                companion_search = Companions.objects.get(id=user_4)
                moreInfo = UserMoreInformation.objects.get(user=companion_search.user)
                if moreInfo.vip:
                    if room.users.exists():
                        messages.error(request, 'Esta habitación ya tiene usuarios, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    elif room.companions.exists():
                        messages.error(request, 'Esta habitación ya tiene acompañantes, no puede ser exclusiva')
                        return redirect('ViewRooms', bus_id)
                    else:
                        room.companions.add(companion_search)
                        user = User.objects.get(username=companion_search.user.username)
                        companions = Companions.objects.filter(user=user)
                        for companion in companions:
                            if companion.id == companion_search.id:
                                pass
                            else:
                                room.companions.add(companion)
                        room.users.add(user)
                        spaces = room.remaining_spaces - 4
                        room.remaining_spaces = spaces
                        room.save()
                        messages.success(request, 'Habitación reservada correctamente')
                        return redirect('ViewRooms', bus_id)
                else:
                    room.companions.add(companion_search)
                    spaces = room.remaining_spaces - 1
                    room.remaining_spaces = spaces
                    room.save()
        messages.success(request, 'Usuarios agregados correctamente a la habitación')
        return redirect('ViewRooms', bus_id)
    
class deleteUserFromRoom(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, room_id, bus_id):
        room = Room.objects.get(id=room_id)
        return render(request, 'deletePeopleOfRooms.html', {'room': room, 'room_id': room_id, 'bus_id': bus_id})

    def post(self, request, room_id, bus_id):
        room = Room.objects.get(id=room_id)
        user_id = request.POST.get('user_id')
        companion_id = request.POST.get('companion_id')
        vaciar = request.POST.get('vaciar')

        if vaciar == 'true':
            room.users.clear()
            room.companions.clear()
            room.remaining_spaces = 4
            room.save()
            messages.success(request, 'Habitación vaciada correctamente')
            return redirect('ViewRooms', bus_id)

        if user_id:
            user = User.objects.get(id=user_id)
            moreInfo = UserMoreInformation.objects.get(user=user)
            if moreInfo.vip:
                room.remaining_spaces = 4
                room.users.clear()
                room.companions.clear()
                room.save()
            else:
                room.remaining_spaces += 1
                room.users.remove(user)
                room.save()

        if companion_id:
            companion = Companions.objects.get(id=companion_id)
            room.remaining_spaces += 1
            room.companions.remove(companion)

        room.save()
        return redirect('ViewRooms', bus_id)
    
class modifyUser(LoginRequiredMixin, View):
    login_url = '/'
    
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        rooms = Room.objects.all()
        fechas = DatesOfTravel.objects.all()
        try:
            moreInformation = UserMoreInformation.objects.get(user=user)
        except UserMoreInformation.DoesNotExist:
            moreInformation = None
        try:
            companions = Companions.objects.filter(user=user)
        except Companions.DoesNotExist:
            companions = None
        return render(request, 'modifyUser.html', {
            'user': user, 
            'rooms': rooms, 
            'dates': fechas, 
            'moreInformation': moreInformation, 
            'companions': companions
        })

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
        radioVip = request.POST.get('RadioVip')

        if people == "Seleccionar...":
            messages.error(request, 'Debe seleccionar la cantidad de personas')
            return redirect('/modify_user/' + str(user_id))

        user.username = request.POST.get('username')
        user.first_name = request.POST.get('name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        moreInfo = UserMoreInformation.objects.get(user=user)

        dates = int(request.POST.get('dates'))
        try:
            date = DatesOfTravel.objects.get(id=dates)
            moreInfo.date_of_travel = date
        except DatesOfTravel.DoesNotExist:
            messages.error(request, 'Seleccione la fecha')
            return redirect('/modify_user/' + str(user_id))

        vip = False
        if people > 1:
            if radioVip == "Yes":
                vip = True
                price = Prices.objects.get(people=people).total
            else:
                vip = False
                price = Prices.objects.get(people=4).price * people
        else:
            if radioVip == "Yes":
                vip = True
                price = Prices.objects.get(people=1).total
            else:
                vip = False
                price = Prices.objects.get(people=4).price

        moreInfo.price = price
        moreInfo.vip = vip

        # Obtener los nombres de los acompañantes desde el formulario
        new_companions = []
        for i in range(1, people):  # iterar desde 1 hasta el número de acompañantes - 1
            name = request.POST.get(f'person{i}')
            if name:
                new_companions.append(name)

        # Actualizar acompañantes
        companions = Companions.objects.filter(user=user)
        companions_to_delete = []

        for companion in companions:
            if companion.name not in new_companions:
                # Si el acompañante actual no está en la lista de nuevos acompañantes, marcarlo para eliminación
                companions_to_delete.append(companion)
            else:
                # Si está, quitarlo de la lista de nuevos acompañantes para que no se vuelva a crear
                new_companions.remove(companion.name)

        # Eliminar los acompañantes que no están en la nueva lista
        for companion in companions_to_delete:
            # También liberar el asiento y la habitación si es necesario
            asientos = Asiento.objects.filter(companion=companion)
            for asiento in asientos:
                asiento.companion = None
                asiento.user = None
                asiento.companion_name = None
                asiento.save()

            try:
                room = Room.objects.get(companions=companion)
                room.companions.remove(companion)
                room.remaining_spaces += 1
                room.save()
            except Room.DoesNotExist:
                pass

            companion.delete()

        # Crear los nuevos acompañantes que no existían antes
        for name in new_companions:
            Companions.objects.create(user=user, name=name)

        moreInfo.people = people
        moreInfo.save()

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
                    price.total = float(price1)
            elif price.people == 2:
                if price2 == '':
                    pass
                elif price2.isspace():
                    pass
                else:
                    price.price = float(price2)
                    price.total = float(price2 * 2)
            elif price.people == 3:
                if price3 == '':
                    pass
                elif price3.isspace():
                    pass
                else:
                    price.price = float(price3)
                    price.total = float(price3 * 3)
            elif price.people == 4:
                if price4 == '':
                    pass
                elif price4.isspace():
                    pass
                else:
                    price.price = float(price4)
                    price.total = float(price4 * 4)
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