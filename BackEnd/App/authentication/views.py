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
from django.core.files.storage import default_storage
from django.db.models import Q, Count
from courses.models import Course, Enrollment
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError


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
@parser_classes([MultiPartParser, FormParser])
def request_instructor(request):
    """User requests to become an instructor with optional documents and details"""
    if request.user.role == 'instructor':
        return Response({'message': 'Already an instructor'}, status=200)
    existing = getattr(request.user, 'instructor_request', None)

    motivation = request.data.get('motivation', '')
    # Support both full_name and name for compatibility with older clients
    full_name = request.data.get(
        'full_name', '') or request.data.get('name', '')
    degree = request.data.get('degree', '')
    certifications = request.data.get('certifications', '')

    uploaded_urls = []
    primary_photo_url = None
    # Handle multiple files (try common keys)
    files = []
    if hasattr(request, 'FILES'):
        files = (
            request.FILES.getlist('files')
            or request.FILES.getlist('file')
            or request.FILES.getlist('documents')
            or []
        )
    for f in files:
        # Try Cloudinary first
        try:
            from cloudinary.uploader import upload as cloudinary_upload
            result = cloudinary_upload(
                f, folder=f"instructors/{request.user.id}")
            if result and 'secure_url' in result:
                uploaded_urls.append(result['secure_url'])
                if not primary_photo_url and str(result.get('resource_type')) == 'image':
                    primary_photo_url = result['secure_url']
                continue
        except Exception:
            # proceed to storage fallback
            ...
        # Fallback to default storage (Cloudinary storage or local media)
        try:
            stored_name = default_storage.save(
                f"instructors/{request.user.id}/{f.name}", f)
            url = default_storage.url(stored_name)
            uploaded_urls.append(url)
            if not primary_photo_url and str(f.content_type or '').startswith('image/'):
                primary_photo_url = url
        except Exception:
            # Ignore individual file upload failures
            pass

    # If we uploaded something but didn't determine a primary photo, pick first
    if not primary_photo_url and uploaded_urls:
        primary_photo_url = uploaded_urls[0]

    ir, _ = InstructorRequest.objects.update_or_create(
        user=request.user,
        defaults={
            'motivation': motivation,
            'full_name': full_name,
            'degree': degree,
            'certifications': certifications,
            'documents': uploaded_urls or (existing.documents if existing else []),
            'photo_url': primary_photo_url or (existing.photo_url if existing else ''),
            'status': 'pending',
            'reviewed_at': None,
            'reviewed_by': None,
        }
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
    return Response({
        'message': 'Request submitted',
        'request': {
            'id': ir.id,
            'user_id': request.user.id,
            'email': request.user.email,
            'full_name': ir.full_name,
            'degree': ir.degree,
            'certifications': ir.certifications,
            'motivation': ir.motivation,
            'documents': ir.documents,
            'photo_url': ir.photo_url,
            'status': ir.status,
        }
    }, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_instructor_request(request):
    ir = getattr(request.user, 'instructor_request', None)
    if not ir:
        return Response({'detail': 'No request found'}, status=404)
    return Response({
        'id': ir.id,
        'user_id': request.user.id,
        'email': request.user.email,
        'full_name': ir.full_name,
        'degree': ir.degree,
        'certifications': ir.certifications,
        'motivation': ir.motivation,
        'documents': ir.documents,
        'photo_url': ir.photo_url,
        'status': ir.status,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_instructor_photo(request):
    file = None
    if hasattr(request, 'FILES'):
        file = request.FILES.get('file') or (
            request.FILES.getlist(
                'files')[0] if request.FILES.getlist('files') else None
        )
    if not file:
        return Response({'error': 'No file provided'}, status=400)
    url = None
    try:
        from cloudinary.uploader import upload as cloudinary_upload
        result = cloudinary_upload(
            file, folder=f"instructors/{request.user.id}")
        url = result.get('secure_url') if result else None
    except Exception:
        url = None
    if not url:
        try:
            stored_name = default_storage.save(
                f"instructors/{request.user.id}/{file.name}", file)
            url = default_storage.url(stored_name)
        except Exception:
            return Response({'error': 'Upload failed'}, status=400)
    ir, _ = InstructorRequest.objects.update_or_create(
        user=request.user,
        defaults={
            'photo_url': url,
        }
    )
    return Response({'photo_url': url, 'id': ir.id})


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
            # New fields for richer admin review UI
            'full_name': getattr(r, 'full_name', ''),
            'degree': getattr(r, 'degree', ''),
            'certifications': getattr(r, 'certifications', ''),
            'documents': getattr(r, 'documents', []),
            'photo_url': getattr(r, 'photo_url', ''),
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


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id: int):
    """Admin-only: permanently delete a user by id."""
    if request.user.role != 'admin':
        return Response({'error': 'Forbidden'}, status=403)

    if request.user.id == user_id:
        return Response({'error': 'You cannot delete your own account.'}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    user.delete()
    return Response({'message': 'User deleted'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_admin(request):
    """Super-admin only: create a new user with a given role.

    Expected body:
      - name (optional): full name, will be split to first/last
      - first_name (optional)
      - last_name (optional)
      - email (required)
      - password (required)
      - confirm_password (required)
      - role (optional, one of 'admin' | 'instructor' | 'student'; default 'admin')
    """
    # Only superusers can create users via this endpoint
    if not getattr(request.user, 'is_superuser', False):
        return Response({'error': 'Forbidden'}, status=403)

    data = request.data or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    confirm_password = data.get('confirm_password') or ''
    name = (data.get('name') or '').strip()
    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()

    if not email:
        return Response({'email': ['This field is required.']}, status=400)
    try:
        django_validate_email(email)
    except DjangoValidationError:
        return Response({'email': ['Enter a valid email address.']}, status=400)

    if not password:
        return Response({'password': ['This field is required.']}, status=400)
    if not confirm_password:
        return Response({'confirm_password': ['This field is required.']}, status=400)
    if password != confirm_password:
        return Response({'confirm_password': ["Passwords don't match."]}, status=400)
    if len(password) < 8:
        return Response({'password': ['Must be at least 8 characters long.']}, status=400)

    # Derive names from 'name' if not provided
    if name and not (first_name or last_name):
        parts = name.split()
        first_name = parts[0]
        last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

    # Ensure email uniqueness
    if User.objects.filter(email=email).exists():
        return Response({'email': ['A user with that email already exists.']}, status=400)

    # Generate a username if not provided, based on email local-part
    base_username = email.split('@')[0][:30] or 'admin'
    candidate = base_username
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        tail = f"{suffix}"
        candidate = f"{base_username[: max(1, 30 - len(tail))]}{tail}"
        suffix += 1

    # Determine role
    role = (data.get('role') or 'admin').strip().lower()
    if role not in {'admin', 'instructor', 'student'}:
        return Response({'role': ['Role must be admin, instructor, or student.']}, status=400)

    # Create the user with chosen role
    user = User.objects.create_user(
        email=email,
        username=candidate,
        first_name=first_name,
        last_name=last_name,
        role=role,
        password=password,
    )

    return Response({
        'message': 'User created successfully',
        'user': UserProfileSerializer(user).data
    }, status=201)
