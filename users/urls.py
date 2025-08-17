from django.urls import path
from .views import *
urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register-user'),
    path('profile/update/', FirebaseProfileUpdateView.as_view(), name='profile-update'),
    path("profile/me/", FirebaseProfileMeView.as_view(), name="firebase-profile-me"),
    path('contact/', ContactCreateView.as_view(), name='contact-form'),
]
