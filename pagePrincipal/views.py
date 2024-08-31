from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from pageLogin.models import *
from Panel_Admin.models import *
from .models import *

# Create your views here.
class home(View):
    def get(self, request):
        return render(request, 'index.html')
    
def information(request):
    return render(request, 'information.html')
    
class profileView(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        user = User.objects.get(username=request.user)
        try:
            moreInformation = UserMoreInformation.objects.get(user=user)
            asientos = Asiento.objects.filter(user=user)
            paid = totalPaidTable.objects.filter(user=user).last()
            total_paid = float(moreInformation.price) - float(paid.totalPaid)
            reservations = Reservation.objects.filter(user=user)
            companions = Companions.objects.filter(user=user)
            return render(request, 'profile.html', {'user': user, 'moreInformation': moreInformation, 'asientos': asientos, 'paid': paid, 'reservations': reservations, 'total_paid': total_paid, 'companions': companions})
        except UserMoreInformation.DoesNotExist:
            paid = totalPaidTable.objects.filter(user=user).last()
            return render(request, 'profile.html', {'user': user, 'paid': paid})
        except Reservation.DoesNotExist:
            paid = totalPaidTable.objects.filter(user=user).last()
            return render(request, 'profile.html', {'user': user, 'paid': paid})
        except Companions.DoesNotExist:
            moreInformation = UserMoreInformation.objects.get(user=user)
            asientos = Asiento.objects.filter(user=user)
            paid = totalPaidTable.objects.filter(user=user).last()
            total_paid = float(moreInformation.price) - float(paid.totalPaid)
            reservations = Reservation.objects.filter(user=user)
            paid = totalPaidTable.objects.filter(user=user).last()
            return render(request, 'profile.html', {'user': user, 'moreInformation': moreInformation, 'asientos': asientos, 'paid': paid, 'reservations': reservations, 'total_paid': total_paid})
