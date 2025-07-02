from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import auth as firebase_auth
from .models import FirebaseUser

@api_view(['POST'])
def register_firebase_user(request):
    id_token = request.headers.get('Authorization', '').split('Bearer ')[-1]
    if not id_token:
        return Response({'detail': 'Missing token'}, status=401)

    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        uid = decoded_token.get('uid')
        name = decoded_token.get('name', '')
        email = decoded_token.get('email')
        phone = decoded_token.get('phone_number', '')

        user, created = FirebaseUser.objects.get_or_create(
            uid=uid,
            defaults={
                'name': name,
                'email': email,
                'phone': phone,
            }
        )

        return Response({
            'uid': uid,
            'email': user.email,
            'created': created
        })

    except Exception as e:
        return Response({'detail': str(e)}, status=400)
# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import FirebaseUser
from .serializers import FirebaseUserSerializer

class FirebaseUserUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_email = request.user.email
        data = request.data
        user_obj, created = FirebaseUser.objects.get_or_create(email=user_email)
        
        serializer = FirebaseUserSerializer(user_obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
