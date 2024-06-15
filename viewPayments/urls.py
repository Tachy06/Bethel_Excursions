from django.urls import path
from .views import *

urlpatterns = [
    path('view_payments', paymentsView.as_view(), name='Payments'),
    path('delete_voucher/<int:voucher_id>', deleteVoucherView.as_view(), name='deleteVoucher'),
]