from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from firebase_admin import auth as firebase_auth
from .models import FirebaseUser
from .serializers import FirebaseUserSerializer
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class FirebaseRegisterView(APIView):
    """Handles Firebase user registration and sync with Django"""
    def post(self, request):
        id_token = request.headers.get('Authorization', '').split('Bearer ')[-1]
        
        if not id_token:
            return Response({'error': 'Authorization token missing'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Verify Firebase token
            decoded_token = firebase_auth.verify_id_token(id_token)
            uid = decoded_token.get('uid')
            email = decoded_token.get('email')
            name = decoded_token.get('name', '')
            phone = decoded_token.get('phone_number', '')
            
            # Create both Django User and FirebaseUser records
            django_user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'is_active': True
                }
            )
            
            # Create corresponding FirebaseUser record
            firebase_user, _ = FirebaseUser.objects.get_or_create(
                uid=uid,
                defaults={
                    'email': email,
                    'name': name,
                    'phone': phone,
                    'user': django_user  # Link to Django user
                }
            )
            
            return Response({
                'uid': uid,
                'email': email,
                'created': created
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    """Handles password reset requests for Firebase users"""
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({'error': 'Email is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Check Firebase first
            try:
                firebase_user = firebase_auth.get_user_by_email(email)
            except firebase_auth.UserNotFoundError:
                return Response({'error': 'User with this email does not exist'},
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Then check/create Django user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'is_active': True
                }
            )
            
            # Generate password reset token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # Build reset URL
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            # Send email
            subject = "Password Reset Request"
            message = f"""
            Hello {email},
            
            You're receiving this email because you requested a password reset.
            
            Please go to the following page:
            {reset_url}
            
            If you didn't request this, please ignore this email.
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response({'message': 'Password reset email sent'}, 
                          status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    """Handles password reset confirmation"""
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            
            if not new_password or len(new_password) < 8:
                return Response({'error': 'Password must be at least 8 characters'}, 
                               status=status.HTTP_400_BAD_REQUEST)
                
            # Update password in Firebase
            try:
                firebase_user = firebase_auth.get_user_by_email(user.email)
                firebase_auth.update_user(firebase_user.uid, password=new_password)
                
                # Also update Django user (though password won't be used for auth)
                user.set_password(new_password)
                user.save()
                
                return Response({'message': 'Password has been reset successfully'}, 
                               status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Firebase password update error: {str(e)}")
                return Response({'error': 'Failed to update password'}, 
                               status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid reset link'}, 
                           status=status.HTTP_400_BAD_REQUEST)

class FirebaseProfileUpdateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        try:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return Response({"detail": "Invalid authorization header"}, status=401)

            id_token = auth_header.split(" ")[1]
            decoded_token = firebase_auth.verify_id_token(id_token)
            uid = decoded_token["uid"]
            
            user = FirebaseUser.objects.get(uid=uid)
            serializer = FirebaseUserSerializer(user, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)

        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            return Response({"detail": str(e)}, status=500)

class FirebaseProfileMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return Response({"detail": "Invalid authorization header"}, status=401)

            id_token = auth_header.split(" ")[1]
            decoded_token = firebase_auth.verify_id_token(id_token)
            uid = decoded_token["uid"]
            
            user = FirebaseUser.objects.get(uid=uid)
            serializer = FirebaseUserSerializer(user)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Profile fetch error: {str(e)}")
            return Response({"detail": str(e)}, status=500)