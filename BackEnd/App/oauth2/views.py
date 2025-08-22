import os
import requests
import random
import string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models import User


class GoogleOAuth2Service:
    """Service class to handle Google OAuth2 operations"""
    
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    def exchange_code_for_tokens(self, code, redirect_uri):
        """Exchange authorization code for access and refresh tokens"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
        }
        
        response = requests.post(self.GOOGLE_TOKEN_URL, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to exchange code: {response.text}")
    
    def get_user_info(self, access_token):
        """Get user information from Google using access token"""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(self.GOOGLE_USER_INFO_URL, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get user info: {response.text}")


@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth_callback(request):
    """
    Handle Google OAuth2 callback
    Accepts authorization code and returns JWT tokens
    """
    try:
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')
        role = request.data.get('role', 'student')  # Default to student if not provided
        
        if not code or not redirect_uri:
            return Response(
                {'error': 'code and redirect_uri are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate role
        if role not in ['student', 'instructor']:
            return Response(
                {'error': 'role must be either student or instructor'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize Google OAuth2 service
        google_service = GoogleOAuth2Service()
        
        # Exchange code for tokens
        token_data = google_service.exchange_code_for_tokens(code, redirect_uri)
        access_token = token_data.get('access_token')
        
        # Get user info from Google
        user_info = google_service.get_user_info(access_token)
        
        def generate_random_username():
            """Generate a random username"""
            while True:
                letters = string.ascii_lowercase + string.digits
                username = ''.join(random.choice(letters) for _ in range(8))
                # Check if username already exists
                if not User.objects.filter(username=username).exists():
                    return username
        
        # Create or get user using existing User model
        user, created = User.objects.get_or_create(
            email=user_info['email'],
            defaults={
                'username': generate_random_username(),
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', ''),
                'role': role,  # Use the selected role
            }
        )
        
        # Update user info if not newly created
        if not created:
            user.first_name = user_info.get('given_name', user.first_name)
            user.last_name = user_info.get('family_name', user.last_name)
            # Update role if user already exists
            user.role = role
            user.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token_jwt = str(refresh.access_token)
        refresh_token_jwt = str(refresh)
        
        # Prepare response data
        response_data = {
            'access_token': access_token_jwt,
            'refresh_token': refresh_token_jwt,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'date_joined': user.date_joined,
                'is_active': user.is_active,
            },
            'google_id': user_info['id'],
            'picture': user_info.get('picture'),
            'locale': user_info.get('locale'),
            'verified_email': user_info.get('verified_email', False),
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def google_auth_url(request):
    """
    Get Google OAuth2 authorization URL
    """
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect_uri = request.GET.get('redirect_uri', 'http://localhost:5173/auth/callback')
    
    # Debug information
    print(f"DEBUG: GOOGLE_CLIENT_ID = {client_id}")
    print(f"DEBUG: GOOGLE_CLIENT_SECRET = {client_secret}")
    print(f"DEBUG: redirect_uri = {redirect_uri}")
    
    if not client_id:
        # For testing purposes, return a mock response
        return Response(
            {
                'error': 'Google Client ID not configured. Please set GOOGLE_CLIENT_ID environment variable.',
                'debug_info': {
                    'client_id_set': bool(client_id),
                    'client_secret_set': bool(client_secret),
                    'redirect_uri': redirect_uri
                }
            }, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    scope = 'openid email profile'
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={scope}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return Response({'auth_url': auth_url}, status=status.HTTP_200_OK)