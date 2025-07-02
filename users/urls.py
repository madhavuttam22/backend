from django.urls import path
from .views import *
urlpatterns = [
    path('profile/',update_profile,name= 'profile')
]
