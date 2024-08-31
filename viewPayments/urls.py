from django.urls import path
from .views import *

urlpatterns = [
    path('view_payments', PaymentsView.as_view(), name='Payments'),
    path('delete_voucher/<int:voucher_id>', DeleteVoucherView.as_view(), name='deleteVoucher'),
]