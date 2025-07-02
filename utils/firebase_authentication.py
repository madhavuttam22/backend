# utils/firebase_authentication.py

import firebase_admin
from firebase_admin import credentials, auth
from rest_framework.exceptions import AuthenticationFailed

# Only initialize once
if not firebase_admin._apps:
    cred = credentials.Certificate("path/to/your/firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)

def verify_firebase_token(token):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise AuthenticationFailed("Invalid Firebase token")
