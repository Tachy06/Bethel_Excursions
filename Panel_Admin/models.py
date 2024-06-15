from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class totalPaidTable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payments = models.FloatField(null=False)
    totalPaid = models.FloatField(null=False)
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'totalPaidTable'
        verbose_name_plural = 'totalPaidTables'
    
