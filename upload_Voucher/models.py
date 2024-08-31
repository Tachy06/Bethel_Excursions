from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class uploadVoucher(models.Model):
    voucher = models.BinaryField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'uploadVoucher'
        verbose_name_plural = 'uploadVouchers'
    
    def __str__(self):
        return self.user.username