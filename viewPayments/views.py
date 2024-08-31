from django.shortcuts import render, redirect
from django.views import View
from upload_Voucher.models import *
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
import os
from django.conf import settings
import base64

# Create your views here.
class PaymentsView(LoginRequiredMixin, View):
    login_url = '/'
    
    def get(self, request):
        user = request.user
        vouchers = uploadVoucher.objects.filter(user=user)

        voucher_files = []
        for voucher in vouchers:
            file_data = voucher.voucher
            if file_data:
                # Convertir datos binarios a base64
                base64_data = base64.b64encode(file_data).decode('utf-8')
                voucher_files.append({
                    'id': voucher.id,
                    'base64_data': base64_data,
                    'date': voucher.date
                })
        
        return render(request, 'viewPaymentsUser.html', {'vouchers': voucher_files})
    
class DeleteVoucherView(LoginRequiredMixin, View):
    login_url = '/'
    def post(self, request, voucher_id):
        try:
            # Obtener el voucher a eliminar
            voucher = uploadVoucher.objects.get(id=voucher_id)
            voucher.delete()  # Eliminar el registro del voucher

            # Mensaje de éxito
            messages.success(request, 'Voucher deleted successfully')
        except uploadVoucher.DoesNotExist:
            # Mensaje de error si el voucher no existe
            messages.error(request, 'Voucher not found')
        
        # Redirigir a la página de pagos
        return redirect('/view_payments')