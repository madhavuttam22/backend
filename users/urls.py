from django.urls import path
from .views import *
urlpatterns = [
    path('register/', register_firebase_user),
    path('profile/update/', FirebaseUserUpdateView.as_view(), name='firebase-profile-update'),
]
