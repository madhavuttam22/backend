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
    


from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .models import Contact
from .serializers import ContactSerializer

class ContactCreateView(generics.CreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()
        
        # Send email to admin
        subject = f"New Contact Form Submission: {contact.subject}"
        message = f"""
        You have received a new contact form submission:
        
        Name: {contact.name}
        Email: {contact.email}
        Phone: {contact.phone or 'Not provided'}
        Subject: {contact.subject}
        Message: {contact.message}
        
        """
        
        html_message = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; }}
                    .content {{ padding: 20px; border: 1px solid #ddd; }}
                    .footer {{ margin-top: 20px; text-align: center; font-size: 0.8em; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>New Contact Form Submission</h2>
                    </div>
                    <div class="content">
                        <p><strong>Name:</strong> {contact.name}</p>
                        <p><strong>Email:</strong> {contact.email}</p>
                        <p><strong>Phone:</strong> {contact.phone or 'Not provided'}</p>
                        <p><strong>Subject:</strong> {contact.subject}</p>
                        <p><strong>Message:</strong></p>
                        <p>{contact.message}</p>
                    </div>
                    <div class="footer">
                        <p>This email was sent from your website's contact form.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
# users/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import Contact
from .serializers import ContactSerializer
import logging

logger = logging.getLogger(__name__)

class ContactCreateView(generics.CreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    throttle_scope = 'contact_form'  # Rate limiting (add to settings.py)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            contact = serializer.save()
            self.send_admin_email(contact)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Contact form failed: {str(e)}", exc_info=True)
            return Response(
                {"error": "Message saved but email failed. We'll contact you soon."},
                status=status.HTTP_201_CREATED
            )

    def send_admin_email(self, contact):
        subject = f"New Contact: {contact.subject}"
        message = f"""
        Name: {contact.name}
        Email: {contact.email}
        Phone: {contact.phone or 'N/A'}
        Message: {contact.message}
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        logger.info(f"Email sent for contact ID: {contact.id}")


# users/views.py
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Generate password reset token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        # Build reset URL
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        # Send email
        subject = "Password Reset Request"
        message = f"""
        Hello {user.email},
        
        You're receiving this email because you requested a password reset for your account.
        
        Please go to the following page and choose a new password:
        {reset_url}
        
        If you didn't request this, please ignore this email.
        
        Thanks,
        Your Ecommerce Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return Response({'message': 'Password reset email sent'}, 
                       status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
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
                
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset successfully'}, 
                           status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid reset link'}, 
                           status=status.HTTP_400_BAD_REQUEST)