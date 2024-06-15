from django.urls import path
from .views import *

urlpatterns = [
    path('upload/', uploadVoucherView.as_view(), name='uploadVoucher'),
]