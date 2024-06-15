from django.urls import path
from .views import *

urlpatterns = [
    path('admin666/', panelAdminView.as_view(), name='Admin'),
    path('delete_user/<int:user_id>/', deleteUser, name='delete_user'),
    path('modify_user/<int:user_id>/', modifyUser.as_view(), name='ModifyUser'),
    path('view_voucher/<int:user_id>/', paymentsAdminView.as_view(), name='Vouchers_Admin'),
    path('total_paid/<int:user_id>/', totalPaid.as_view(), name='TotalPaid'),
    path('view_payments_admin/<int:user_id>/', viewPaymentsAdmin.as_view(), name='ViewPaymentsAdmin'),
    path('delete_payments_admin/<int:total_id>/<int:user_id>/', deletePaymentsAdmin, name='DeletePaymentsAdmin'),
    path('view_bus/<int:bus_id>/', viewBus.as_view(), name='ViewBus'),
    path('make_available/<int:asiento_id>/', makeAvailable.as_view(), name='makeAvailable'),
    path('define_seats/<int:seat_id>/', defineSeat.as_view(), name='DefineSeat'),
    path('addSeats/<int:bus_id>/', addSeats.as_view(), name='AddSeats'),
    path('view_rooms/', viewRooms.as_view(), name='ViewRooms'),
    path('add_rooms/', addRooms.as_view(), name='AddRooms'),
    path('modifyPrices/', modifyPrices.as_view(), name='ModifyPrices'),
    path('modifyDates/', modifyDates.as_view(), name='ModifyDates'),
    path('createAdmin/', createAdmin.as_view(), name='CreateAdmin'),
]