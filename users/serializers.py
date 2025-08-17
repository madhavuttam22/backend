# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FirebaseUser, Contact
from django.conf import settings
from django.core.mail import send_mail
import logging



# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

RegisterUser = get_user_model()

class RegisterUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=RegisterUser.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = RegisterUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone', 'password', 'password2'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        user = RegisterUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

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