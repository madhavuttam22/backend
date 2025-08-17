# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FirebaseUser, Contact
from django.conf import settings
from django.core.mail import send_mail
import logging




# Configure logger
logger = logging.getLogger(__name__)

class UserProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='profile.phone', required=False)
    address = serializers.CharField(source='profile.address', required=False)
    avatar = serializers.ImageField(source='profile.avatar', required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'avatar']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        instance = super().update(instance, validated_data)

        profile = instance.profile
        profile.phone = profile_data.get('phone', profile.phone)
        profile.address = profile_data.get('address', profile.address)
        if 'avatar' in profile_data:
            profile.avatar = profile_data['avatar']
        profile.save()

        return instance


class FirebaseUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = FirebaseUser
        fields = ['id', 'uid', 'email', 'name', 'avatar', 'phone', 'address']

    def get_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message', 'created_at']