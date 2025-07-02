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
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import FirebaseUser
from .serializers import FirebaseUserSerializer

# class FirebaseUserUpdateView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def put(self, request):
#         user_email = request.user.email
#         data = request.data
#         try:
#             user_obj, created = FirebaseUser.objects.get_or_create(email=user_email)
#         except FirebaseUser.MultipleObjectsReturned:
#             return Response({'detail': 'Multiple users found with same email'}, status=status.HTTP_400_BAD_REQUEST)

#         serializer = FirebaseUserSerializer(user_obj, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "name": f"{serializer.data.get('first_name')} {serializer.data.get('last_name')}",
#                 "email": serializer.data.get("email"),
#                 "phone": serializer.data.get("phone"),
#                 "address": serializer.data.get("address"),
#                 "avatar": serializer.data.get("avatar"),
#             }, status=status.HTTP_200_OK)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, parsers
from firebase_admin import auth as firebase_auth
from .models import FirebaseUser
from .serializers import FirebaseUserSerializer

class FirebaseProfileUpdateView(APIView):
    parser_classes = [parsers.JSONParser]

    permission_classes = [permissions.AllowAny]  # Or custom Firebase permission

    def put(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"detail": "Authentication credentials were not provided."}, status=401)

        id_token = auth_header.split("Bearer ")[-1]

        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            email = decoded_token.get("email")
            uid = decoded_token.get("uid")
        except Exception as e:
            return Response({"detail": str(e)}, status=401)

        try:
            user, created = FirebaseUser.objects.get_or_create(email=email, uid=uid)
        except Exception as e:
            return Response({"detail": f"DB Error: {str(e)}"}, status=500)

        serializer = FirebaseUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
