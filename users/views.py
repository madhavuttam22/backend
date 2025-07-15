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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from firebase_admin import auth as firebase_auth
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class PasswordResetRequestView(APIView):
    """Handles password reset requests with rate limiting"""
    
    @method_decorator(ratelimit(key='ip', rate='5/h', method='POST'))
    def post(self, request):
        was_limited = getattr(request, 'limited', False)
        if was_limited:
            return Response(
                {'error': 'Too many requests. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
            
        email = request.data.get('email', '').strip().lower()
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check if user exists in Firebase
            try:
                firebase_user = firebase_auth.get_user_by_email(email)
            except firebase_auth.UserNotFoundError:
                logger.warning(f"Password reset attempt for non-existent email: {email}")
                return Response(
                    {'error': 'If this email exists, a reset link has been sent'},
                    status=status.HTTP_200_OK
                )
            
            # Get or create Django user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'is_active': True
                }
            )
            
            # Generate tokens
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # Build reset URL
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            # Send email
            send_mail(
                'Password Reset Request',
                f'Use this link to reset your password: {reset_url}\n\n'
                f'This link will expire in 24 hours.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            logger.info(f"Password reset email sent to {email}")
            return Response(
                {'message': 'If this email exists, a reset link has been sent'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Password reset error for {email}: {str(e)}")
            return Response(
                {'error': 'An error occurred. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PasswordResetConfirmView(APIView):
    """Handles password reset confirmation with validation"""
    
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user is None or not default_token_generator.check_token(user, token):
            logger.warning(f"Invalid password reset link used: uidb64={uidb64}")
            return Response(
                {'error': 'Invalid or expired reset link. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')
        
        # Validation
        if not new_password or len(new_password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if new_password != confirm_password:
            return Response(
                {'error': 'Passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Optional: Add more password strength checks
        if not any(c.isupper() for c in new_password):
            return Response(
                {'error': 'Password must contain at least one uppercase letter'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not any(c.islower() for c in new_password):
            return Response(
                {'error': 'Password must contain at least one lowercase letter'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not any(c.isdigit() for c in new_password):
            return Response(
                {'error': 'Password must contain at least one number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Update password in Firebase
            firebase_user = firebase_auth.get_user_by_email(user.email)
            firebase_auth.update_user(firebase_user.uid, password=new_password)
            
            # Update Django user (for consistency)
            user.set_password(new_password)
            user.save()
            
            logger.info(f"Password successfully reset for user: {user.email}")
            return Response(
                {'message': 'Password has been reset successfully'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Password reset failed for {user.email}: {str(e)}")
            return Response(
                {'error': 'Failed to update password. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

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