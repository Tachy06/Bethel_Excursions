from django.shortcuts import render, redirect
from django.views import View
from upload_Voucher.models import *
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
import os
from django.conf import settings

# Create your views here.
class paymentsView(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        user = User.objects.get(username=request.user)
        vouchers = uploadVoucher.objects.filter(user=user)
        return render(request, 'viewPaymentsUser.html', {'vouchers': vouchers})
    
class deleteVoucherView(LoginRequiredMixin, View):
    login_url = '/'
    def post(self, request, voucher_id):
        voucher = uploadVoucher.objects.get(id=voucher_id)
        file_path = os.path.join(settings.MEDIA_ROOT, str(voucher.voucher))
        if os.path.exists(file_path):
            os.remove(file_path)
            voucher.delete()
            messages.success(request, 'Voucher deleted successfully')
        else:
            messages.error(request, 'Voucher not found')
        return redirect('/view_payments')