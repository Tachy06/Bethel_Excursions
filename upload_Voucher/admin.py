from django.contrib import admin
from . models import *

# Register your models here.
class VoucherAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'voucher', 'date']

admin.site.register(uploadVoucher, VoucherAdmin)