from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages

# Create your views here.
class uploadVoucherView(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        return render(request, 'uploadFile.html')
    def post(self, request):
        user = User.objects.get(username=request.user)
        upload = uploadVoucher.objects.create(user=user)
        if 'voucher' in request.FILES:
            voucher = request.FILES['voucher']
            binary_data = voucher.read()
            upload.voucher = binary_data
            upload.save()
        messages.success(request, 'Voucher uploaded successfully')
        return redirect('/upload/')