import os
from firebase_admin import auth as firebase_auth, credentials
import firebase_admin
from django.http import JsonResponse

# Absolute path to the key inside cart/firebase/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # points to `backend/`
CRED_PATH = os.path.join(BASE_DIR, 'cart', 'firebase', 'serviceAccountKey.json')

if not firebase_admin._apps:
    cred = credentials.Certificate(CRED_PATH)
    firebase_admin.initialize_app(cred)

def firebase_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        id_token = request.headers.get("Authorization")
        if not id_token or not id_token.startswith("Bearer "):
            return JsonResponse({"error": "Authorization token missing"}, status=401)

        try:
            decoded_token = firebase_auth.verify_id_token(id_token.split(" ")[1])
            request.firebase_user = decoded_token
            return view_func(request, *args, **kwargs)
        except Exception as e:
            print("Firebase auth error:", e)
            return JsonResponse({"error": "Invalid or expired token"}, status=401)

    return wrapper
