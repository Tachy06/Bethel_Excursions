from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', panelAdminView.as_view(), name='Admin'),
    path('delete_user/<int:user_id>/', deleteUser, name='delete_user'),
    path('modify_user/<int:user_id>/', modifyUser.as_view(), name='ModifyUser'),
    path('view_voucher/<int:user_id>/', paymentsAdminView.as_view(), name='Vouchers_Admin'),
    path('delete_voucher/<int:voucher_id>/', deleteVoucher, name='DeleteVoucherAdmin'),
    path('total_paid/<int:user_id>/', totalPaid.as_view(), name='TotalPaid'),
    path('view_payments_admin/<int:user_id>/', viewPaymentsAdmin.as_view(), name='ViewPaymentsAdmin'),
    path('delete_payments_admin/<int:total_id>/<int:user_id>/', deletePaymentsAdmin, name='DeletePaymentsAdmin'),
    path('view_bus/<int:bus_id>/', viewBus.as_view(), name='ViewBus'),
    path('delete_seat/<int:asiento_id>/bus/<int:bus_id>/', deleteSeat, name='DeleteSeat'),
    path('make_available/<int:asiento_id>/', makeAvailable.as_view(), name='makeAvailable'),
    path('define_seats/<int:seat_id>/', defineSeat.as_view(), name='DefineSeat'),
    path('addSeats/<int:bus_id>/', addSeats.as_view(), name='AddSeats'),
    path('view_rooms/<int:room_id>/', viewRooms.as_view(), name='ViewRooms'),
    path('delete_room/bus/<int:bus_id>/room/<int:room_id>/', DeleteRoom.as_view(), name='DeleteRoom'),
    path('add_rooms/bus/<int:bus_id>/', addRooms.as_view(), name='AddRooms'),
    path('addUsersToRoom/<int:room_id>/bus/<int:bus_id>/', addUserToRoom.as_view(), name='AddUsersToRoom'),
    path('delete_people_from_room_view/<int:room_id>/bus/<int:bus_id>/', deleteUserFromRoom.as_view(), name='DeletePeopleFromRoom'),
    path('modifyPrices/', modifyPrices.as_view(), name='ModifyPrices'),
    path('modifyDates/', modifyDates.as_view(), name='ModifyDates'),
    path('createAdmin/', createAdmin.as_view(), name='CreateAdmin'),
]