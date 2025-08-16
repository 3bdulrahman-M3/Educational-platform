from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    GoogleAuthSerializer,
    GoogleCompleteSerializer,
    RoleUpdateSerializer
)
from .models import User
from .services import verify_google_token
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
import json
from google.oauth2 import id_token
from google.auth.transport import requests
import os

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):

    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User registered successfully',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):

    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    """
    Handle Google OAuth authentication
    Returns user data and isNewUser flag
    """
    try:
        data = request.data
        token = data.get('token')

        if not token:
            return Response({
                'error': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verify Google token and get user info
        try:
            user_info = verify_google_token(token)
        except ValidationError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        try:
            user = User.objects.get(email=user_info['email'])
            is_new_user = False
        except User.DoesNotExist:
            # Create user without role (will be set later)
            try:
                user = User.objects.create_user(
                    email=user_info['email'],
                    first_name=user_info['first_name'],
                    last_name=user_info['last_name'],
                    google_id=user_info['google_id'],
                    username=user_info['email'].split(
                        '@')[0] + '_' + str(uuid.uuid4())[:8]
                )
                is_new_user = True
            except Exception as e:
                return Response({
                    'error': f'Failed to create user: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Generate tokens
        try:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
        except Exception as e:
            return Response({
                'error': f'Failed to generate tokens: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'role': getattr(user, 'role', None),
                'date_joined': user.date_joined,
                'google_id': getattr(user, 'google_id', None),
                'picture': getattr(user, 'picture', None)
            },
            'tokens': {
                'access': access_token,
                'refresh': refresh_token
            },
            'isNewUser': is_new_user
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Google auth error: {str(e)}")  # Add this for debugging
        return Response({
            'error': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_complete(request):
    """
    Complete Google registration by updating user with role
    """
    try:
        data = request.data
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        google_id = data.get('google_id')
        role = data.get('role')

        if not all([email, first_name, last_name, google_id, role]):
            return Response({
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find the user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Update user with role
        user.role = role
        user.save()

        # Generate new tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'role': user.role,
                'date_joined': user.date_joined,
                'google_id': user.google_id,
                'picture': getattr(user, 'picture', None)
            },
            'tokens': {
                'access': access_token,
                'refresh': refresh_token
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user(request):
    """
    Get current user information
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):

    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):

    serializer = UserProfileSerializer(
        request.user, data=request.data, partial=True)
    if serializer.is_valid():
        # Check if role is being updated
        role_changed = 'role' in request.data and request.data['role'] != request.user.role
        old_role = request.user.role if role_changed else None

        serializer.save()

        response_data = {
            'message': 'Profile updated successfully',
            'user': serializer.data
        }

        # If role was changed, generate new tokens and add message
        if role_changed:
            refresh = RefreshToken.for_user(request.user)
            response_data[
                'message'] = f'Profile updated successfully. Role changed from {old_role} to {request.user.role}'
            response_data['tokens'] = {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }

        return Response(response_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_role(request):
    """
    Update existing user's role when they didn't choose during registration
    """
    try:
        data = request.data
        email = data.get('email')
        role = data.get('role')

        if not all([email, role]):
            return Response({
                'error': 'Missing required fields: email and role'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate role
        if role not in ['student', 'instructor']:
            return Response({
                'error': 'Invalid role. Must be either "student" or "instructor"'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find the user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Update user role
        user.role = role
        user.save()

        # Generate new tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'role': user.role,
                'date_joined': user.date_joined,
                'google_id': user.google_id,
                'picture': getattr(user, 'picture', None)
            },
            'tokens': {
                'access': access_token,
                'refresh': refresh_token
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout user (blacklist refresh token)
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
