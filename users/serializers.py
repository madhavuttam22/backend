from rest_framework import serializers
from django.contrib.auth.models import User

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


# serializers.py
from rest_framework import serializers
from .models import FirebaseUser

class FirebaseUserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)
    class Meta:
        model = FirebaseUser
        fields = ['first_name','last_name','email','phone','address','avatar']

