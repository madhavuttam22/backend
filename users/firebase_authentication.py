# users/firebase_authentication.py
from rest_framework.authentication import BaseAuthentication
from firebase_admin import auth as firebase_auth
from .models import FirebaseUser

class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        id_token = auth_header.split('Bearer ')[-1]

        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            uid = decoded_token.get('uid')
            email = decoded_token.get('email')
            name = decoded_token.get('name', '')
            phone = decoded_token.get('phone_number', '')

            user, created = FirebaseUser.objects.get_or_create(
                uid=uid,
                defaults={'email': email, 'name': name, 'phone': phone}
            )
            return (user, None)

        except Exception:
            return None
