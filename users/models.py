from django.db import models

# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class RegisterUser(AbstractUser):
    # Additional fields beyond default User model
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Firebase specific fields if needed
    firebase_uid = models.CharField(max_length=128, blank=True, null=True, unique=True)
    
    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Registered User"
        verbose_name_plural = "Registered Users"

class FirebaseUser(models.Model):
    uid = models.CharField(max_length=128, unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.email

from django.db import models
from django.utils import timezone

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_resolved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"