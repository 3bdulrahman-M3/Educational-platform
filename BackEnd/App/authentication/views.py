from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .models import User
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlencode
from django.utils import timezone


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
                # 'refresh': str(refresh),
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
                # 'refresh': str(refresh),
            }
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):

    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_profile(request):

    serializer = UserProfileSerializer(
        request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    reset_token = serializer.save()

    # Always return success message to avoid email enumeration
    if reset_token:
        base_frontend_url = getattr(
            settings, 'FRONTEND_BASE_URL', 'http://localhost:5173')
        reset_path = '/reset-password'
        query = urlencode({'token': reset_token.token})
        reset_url = f"{base_frontend_url}{reset_path}?{query}"

        subject = 'Reset your password'
        message = f"Use the following link to reset your password. This link expires in 15 minutes.\n\n{reset_url}"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL',
                             'no-reply@example.com')
        recipient_list = [reset_token.user.email]

        try:
            send_mail(subject, message, from_email,
                      recipient_list, fail_silently=True)
        except Exception:
            # Silently ignore email errors to prevent leaking details
            pass

    return Response({'message': 'If the email exists, a reset link has been sent.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        try:
            user_email = serializer.reset_token.user.email
            subject = 'Your password was changed'
            message = 'This is a confirmation that your password has been changed successfully.'
            from_email = getattr(
                settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')
            send_mail(subject, message, from_email, [
                      user_email], fail_silently=True)
        except Exception:
            pass
        return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
