from django.urls import path
from .views import *

urlpatterns = [
    path('', home.as_view(), name='home'),
    path('profile/', profileView.as_view(), name='Profile'),
]