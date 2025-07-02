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
# views.py
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import auth as firebase_auth
from .models import FirebaseUser
from .serializers import FirebaseUserSerializer
from rest_framework import permissions
class FirebaseProfileUpdateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]  # or IsAuthenticated if token validated

    def put(self, request):
        # ✅ Step 1: Extract Firebase token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"detail": "Authorization header missing"}, status=403)
        
        id_token = auth_header.split("Bearer ")[1]

        try:
            # ✅ Step 2: Verify token
            decoded_token = firebase_auth.verify_id_token(id_token)
            uid = decoded_token.get("uid")
            email = decoded_token.get("email")
        except Exception as e:
            return Response({"detail": "Invalid or expired token"}, status=403)

        # ✅ Step 3: Get or create user using email and uid
        user, _ = FirebaseUser.objects.get_or_create(uid=uid, defaults={"email": email})

        # ✅ Step 4: Update profile with form data (partial=True allows partial update)
        serializer = FirebaseUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)