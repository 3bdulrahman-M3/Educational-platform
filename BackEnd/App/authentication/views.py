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
from .models import User, InstructorRequest
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlencode
from django.utils import timezone
from notifications.views import send_notification
from django.db.models import Q, Count
from courses.models import Course, Enrollment


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_instructor(request):
    """User requests to become an instructor"""
    if request.user.role == 'instructor':
        return Response({'message': 'Already an instructor'}, status=200)
    existing = getattr(request.user, 'instructor_request', None)
    if existing and existing.status == 'pending':
        return Response({'message': 'Request already pending'}, status=200)
    motivation = request.data.get('motivation', '')
    ir, _ = InstructorRequest.objects.update_or_create(
        user=request.user,
        defaults={'motivation': motivation, 'status': 'pending',
                  'reviewed_at': None, 'reviewed_by': None}
    )
    # notify admins
    try:
        admin_ids = list(User.objects.filter(
            role='admin').values_list('id', flat=True))
        for admin_id in admin_ids:
            send_notification(
                sender_id=request.user.id,
                receiver_id=admin_id,
                notification_type='announcement',
                title='Instructor Request',
                message=f"{request.user.get_full_name() or request.user.email} requested to become an instructor."
            )
    except Exception:
        pass
    return Response({'message': 'Request submitted'}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_instructor_requests(request):
    if request.user.role != 'admin':
        return Response({'error': 'Forbidden'}, status=403)
    pending = InstructorRequest.objects.select_related(
        'user').order_by('-created_at')
    data = [
        {
            'id': r.id,
            'user_id': r.user_id,
            'email': r.user.email,
            'name': r.user.get_full_name(),
            'motivation': r.motivation,
            'status': r.status,
            'created_at': r.created_at,
        }
        for r in pending
    ]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_instructor(request, request_id):
    if request.user.role != 'admin':
        return Response({'error': 'Forbidden'}, status=403)
    req = InstructorRequest.objects.filter(
        id=request_id).select_related('user').first()
    if not req:
        return Response({'error': 'Request not found'}, status=404)
    req.status = 'approved'
    req.reviewed_at = timezone.now()
    req.reviewed_by = request.user
    req.save(update_fields=['status', 'reviewed_at', 'reviewed_by'])
    # promote user
    req.user.role = 'instructor'
    req.user.save(update_fields=['role'])
    try:
        send_notification(
            sender_id=request.user.id,
            receiver_id=req.user_id,
            notification_type='announcement',
            title='Instructor Approved',
            message='You are now an instructor.'
        )
    except Exception:
        pass
    return Response({'message': 'Instructor approved'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_instructor(request, request_id):
    if request.user.role != 'admin':
        return Response({'error': 'Forbidden'}, status=403)
    req = InstructorRequest.objects.filter(
        id=request_id).select_related('user').first()
    if not req:
        return Response({'error': 'Request not found'}, status=404)
    reason = request.data.get('reason', '')
    req.status = 'rejected'
    req.reviewed_at = timezone.now()
    req.reviewed_by = request.user
    req.save(update_fields=['status', 'reviewed_at', 'reviewed_by'])
    try:
        send_notification(
            sender_id=request.user.id,
            receiver_id=req.user_id,
            notification_type='announcement',
            title='Instructor Request Rejected',
            message=f'Reason: {reason}'
        )
    except Exception:
        pass
    return Response({'message': 'Instructor rejected'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """Admin-only: list users with optional filters

    Query params:
      - role: 'student' | 'instructor' | 'admin'
      - search: name or email contains
      - status: for students 'active'|'inactive'; for instructors 'approved'|'pending'
    """
    if request.user.role != 'admin':
        return Response({'error': 'Forbidden'}, status=403)

    role = request.query_params.get('role')
    search = request.query_params.get('search', '').strip()
    status_filter = request.query_params.get('status')

    users = User.objects.all().order_by('-date_joined')
    if role:
        users = users.filter(role=role)

    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(username__icontains=search)
        )

    # Map domain-specific statuses
    if role == 'student' and status_filter:
        # Treat is_active as student status
        if status_filter.lower() == 'active':
            users = users.filter(is_active=True)
        elif status_filter.lower() == 'inactive':
            users = users.filter(is_active=False)
    elif role == 'instructor' and status_filter:
        # Consider instructors "approved" if role == instructor.
        if status_filter.lower() == 'approved':
            users = users.filter(role='instructor')
        elif status_filter.lower() == 'pending':
            # pending instructor requests
            pending_ids = InstructorRequest.objects.filter(
                status='pending').values_list('user_id', flat=True)
            users = users.filter(id__in=list(pending_ids))

    serializer = UserProfileSerializer(users, many=True)
    data = serializer.data

    # Build maps for computed counts/status
    user_ids = list(users.values_list('id', flat=True))

    if role == 'student':
        enroll_counts = dict(
            Enrollment.objects.filter(student_id__in=user_ids)
            .values_list('student_id')
            .annotate(cnt=Count('id'))
        ) if user_ids else {}
        for item in data:
            uid = item['id']
            item['enrolled_courses_count'] = int(enroll_counts.get(uid, 0))
            item['status'] = 'Active' if users.filter(
                id=uid, is_active=True).exists() else 'Inactive'

    if role == 'instructor':
        approved_counts = dict(
            Course.objects.filter(
                instructor_id__in=user_ids, status='approved')
            .values_list('instructor_id')
            .annotate(cnt=Count('id'))
        ) if user_ids else {}
        # pending ids via InstructorRequest
        pending_ids = set(InstructorRequest.objects.filter(status='pending', user_id__in=user_ids)
                          .values_list('user_id', flat=True))
        for item in data:
            uid = item['id']
            item['approved_courses_count'] = int(approved_counts.get(uid, 0))
            item['status'] = 'Pending' if uid in pending_ids else 'Approved'

    return Response(data)
