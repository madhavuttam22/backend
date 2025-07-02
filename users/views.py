from firebase_admin import auth as firebase_auth
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['PUT'])
def update_profile(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({'detail': 'Unauthorized'}, status=401)

    id_token = auth_header.split(' ')[1]
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        # Proceed with updating profile for user with `uid`
    except Exception as e:
        return Response({'detail': 'Invalid token'}, status=401)
