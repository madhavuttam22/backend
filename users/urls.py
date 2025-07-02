from django.urls import path
from .views import *
urlpatterns = [
    # path('register/', register_firebase_user),
    path('profile/update/', FirebaseProfileUpdateView.as_view(), name='profile-update'),
    path("profile/me/", FirebaseProfileMeView.as_view(), name="firebase-profile-me"),
]
