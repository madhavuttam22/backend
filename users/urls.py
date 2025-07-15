from django.urls import path
from .views import (
    FirebaseRegisterView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    FirebaseProfileUpdateView,
    FirebaseProfileMeView
)

urlpatterns = [
    path('register/', FirebaseRegisterView.as_view(), name='firebase-register'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(), 
         name='password-reset-confirm'),
    path('profile/update/', FirebaseProfileUpdateView.as_view(), name='profile-update'),
    path('profile/me/', FirebaseProfileMeView.as_view(), name="firebase-profile-me"),
]