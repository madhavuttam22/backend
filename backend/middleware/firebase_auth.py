import os
import json
import firebase_admin
from firebase_admin import auth, credentials
from django.http import JsonResponse

class FirebaseAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # Initialize Firebase only once, and only if not already initialized
        if not firebase_admin._apps:
            firebase_json = os.getenv("FIREBASE_CREDENTIAL_JSON")
            if firebase_json:
                try:
                    firebase_dict = json.loads(firebase_json)
                    cred = credentials.Certificate(firebase_dict)
                    firebase_admin.initialize_app(cred)
                except Exception as e:
                    print(f"Warning: Firebase init failed: {e}")
            else:
                print("Warning: FIREBASE_CREDENTIAL_JSON not set. Firebase auth will not work.")

    def __call__(self, request):
        authorization = request.headers.get('Authorization')

        if authorization and authorization.startswith('Bearer '):
            id_token = authorization.split('Bearer ')[1]
            try:
                decoded_token = auth.verify_id_token(id_token)
                request.firebase_user = decoded_token
            except Exception:
                return JsonResponse({"detail": "Invalid Firebase token"}, status=401)

        return self.get_response(request)
