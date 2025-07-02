from firebase_admin import auth as firebase_auth
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import base64

User = get_user_model()

@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_profile(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({'detail': 'Unauthorized'}, status=401)

    id_token = auth_header.split(' ')[1]
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # You must have a user model that stores uid
        user, created = User.objects.get_or_create(firebase_uid=uid)

        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        email = request.data.get('email', '')
        phone = request.data.get('phone', '')
        address = request.data.get('address', '')

        if email:
            user.email = email
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if phone:
            user.phone = phone
        if address:
            user.address = address

        # Avatar handling
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']

        user.save()

        return Response({
            "name": f"{user.first_name} {user.last_name}".strip(),
            "email": user.email,
            "phone": user.phone,
            "address": user.address,
            "avatar": user.avatar.url if user.avatar else ""
        }, status=200)

    except Exception as e:
        print("Profile Update Error:", e)
        return Response({'detail': 'Internal Server Error'}, status=500)
