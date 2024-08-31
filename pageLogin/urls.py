from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='Register'),
    path('login/', loginView.as_view(), name='Login'),
    path('logout/', logoutView, name='Logout'),
    path('what_price/', what_price, name='What_Price'),
    path('terms_and_conditions/', terms_and_conditions, name='Terms_and_Conditions'),
]