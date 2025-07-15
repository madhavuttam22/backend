from django.urls import path
from .views import *
urlpatterns = [
    # path('register/', register_firebase_user),
    path('profile/update/', FirebaseProfileUpdateView.as_view(), name='profile-update'),
    path("profile/me/", FirebaseProfileMeView.as_view(), name="firebase-profile-me"),
    path('contact/', ContactCreateView.as_view(), name='contact-form'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/',PasswordResetConfirmView.as_view(),name='password-reset-confirm'),
]
