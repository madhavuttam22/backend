# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from firebase_admin import auth as firebase_auth
# from .models import FirebaseUser

# @api_view(['POST'])
# def register_firebase_user(request):
#     id_token = request.headers.get('Authorization', '').split('Bearer ')[-1]
#     if not id_token:
#         return Response({'detail': 'Missing token'}, status=401)

#     try:
#         decoded_token = firebase_auth.verify_id_token(id_token)
#         uid = decoded_token.get('uid')
#         name = decoded_token.get('name', '')
#         email = decoded_token.get('email')
#         phone = decoded_token.get('phone_number', '')

#         user, created = FirebaseUser.objects.get_or_create(
#             uid=uid,
#             defaults={
#                 'name': name,
#                 'email': email,
#                 'phone': phone,
#             }
#         )

#         return Response({
#             'uid': uid,
#             'email': user.email,
#             'created': created
#         })

#     except Exception as e:
#         return Response({'detail': str(e)}, status=400)


# users/views.py
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, permissions
from firebase_admin import auth as firebase_auth
from .models import FirebaseUser
from .serializers import FirebaseUserSerializer

class FirebaseProfileUpdateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]  # adjust as needed

    def put(self, request):
        try:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return Response({"detail": "Invalid authorization header"}, status=401)

            id_token = auth_header.split(" ")[1]
            decoded_token = firebase_auth.verify_id_token(id_token)
            uid = decoded_token["uid"]
            email = decoded_token.get("email", "")

            if not email:
                return Response({"detail": "Email not found in token"}, status=400)

            user, _ = FirebaseUser.objects.get_or_create(uid=uid, defaults={"email": email})
            serializer = FirebaseUserSerializer(user, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            else:
                return Response({"errors": serializer.errors}, status=400)

        except firebase_auth.InvalidIdTokenError:
            return Response({"detail": "Invalid ID token"}, status=403)
        except Exception as e:
            return Response({"detail": str(e)}, status=500)

# users/views.py
# users/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import FirebaseUser
from .serializers import FirebaseUserSerializer
from utils.firebase_authentication import verify_firebase_token

class FirebaseProfileMeView(APIView):
    permission_classes = [AllowAny]  # Use AllowAny if you're using token manually

    def get(self, request):
        token = request.META.get("HTTP_AUTHORIZATION", "").split("Bearer ")[-1]
        if not token:
            return Response({"detail": "Authorization header missing"}, status=400)

        try:
            decoded = verify_firebase_token(token)
            email = decoded.get("email")
            uid = decoded.get("user_id")
        except Exception as e:
            return Response({"detail": "Invalid Firebase token"}, status=401)

        user = FirebaseUser.objects.filter(email=email, uid=uid).first()
        if not user:
            return Response({"detail": "User not found"}, status=404)

        serializer = FirebaseUserSerializer(user)
        return Response(serializer.data)