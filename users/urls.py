from django.urls import path
from .views import *
urlpatterns = [
    # path('register/', register_firebase_user),
    path('api/profile/', FirebaseUserUpdateView.as_view(), name='profile-update'),
]
