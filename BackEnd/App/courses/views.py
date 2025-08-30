from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, parsers, generics
from .models import Course, Enrollment, Category, Video
from .serializers import CourseSerializer, EnrollmentSerializer, CategorySerializer, VideoSerializer
from exams.serializers import ExamSerializer
from exams.models import Exam
from authentication.serializers import UserProfileSerializer
from authentication.models import User
from django.db import models
from django.db.models import Q
from notifications.views import send_notification
from django.db.models import Q
from notifications.views import send_notification
import stripe
import os
from dotenv import load_dotenv

# Create your views here.

load_dotenv()
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = STRIPE_SECRET_KEY


def is_enrolled(user, course):
    return Enrollment.objects.filter(student=user, course=course).exists()


@api_view(['GET'])
@permission_classes([AllowAny])
def get_instructors(request):
    search = request.query_params.get('search', '')
    instructors = User.objects.filter(role='instructor')
    if search:
        instructors = instructors.filter(
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(email__icontains=search)
        )
    from .serializers import InstructorSerializer
    serializer = InstructorSerializer(instructors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_courses(request):
    if request.user.role != 'admin':
        return Response({'error': 'Forbidden'}, status=403)
    pending = Course.objects.filter(status='pending')
    return Response(CourseSerializer(pending, many=True, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_instructor_with_courses(request, instructor_id):
    try:
        instructor = User.objects.get(id=instructor_id, role='instructor')
    except User.DoesNotExist:
        return Response({'error': 'Instructor not found'}, status=status.HTTP_404_NOT_FOUND)
    from .serializers import InstructorSerializer, CourseSerializer
    instructor_data = InstructorSerializer(instructor).data
    courses = instructor.created_courses.all()
    courses_data = CourseSerializer(courses, many=True, context={
                                    'request': request}).data  # Pass context
    instructor_data['courses'] = courses_data
    return Response(instructor_data)


# @parser_classes([parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course(request):
    if request.user.role != 'instructor':
        return Response({'error': 'Only instructors can create courses.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = CourseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(instructor=request.user, status='pending')
        # notify admin(s) about pending course
        try:
            admin_ids = list(User.objects.filter(
                role='admin').values_list('id', flat=True))
            for admin_id in admin_ids:
                send_notification(
                    sender_id=request.user.id,
                    receiver_id=admin_id,
                    notification_type='course_update',
                    title='Course Approval Needed',
                    message=f"'{request.user.get_full_name() or request.user.email}' submitted course '{serializer.data.get('title')}' for approval"
                )
        except Exception:
            pass
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @parser_classes([parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser])
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_course(request, pk):
    if request.user.role != 'instructor':
        return Response({'error': 'Only instructors can update courses'}, status=status.HTTP_403_FORBIDDEN)
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    # reset to pending on updates
    serializer = CourseSerializer(course, data=request.data, partial=True)
    if serializer.is_valid():
        updated = serializer.save(status='pending')
        # notify admins about re-approval
        try:
            admin_ids = list(User.objects.filter(
                role='admin').values_list('id', flat=True))
            for admin_id in admin_ids:
                send_notification(
                    sender_id=request.user.id,
                    receiver_id=admin_id,
                    notification_type='course_update',
                    title='Course Requires Re-Approval',
                    message=f"'{request.user.get_full_name() or request.user.email}' updated course '{updated.title}' and it requires approval again"
                )
        except Exception:
            pass
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_approve_course(request, pk):
    if request.user.role != 'admin':
        return Response({'error': 'Only admin can approve courses'}, status=status.HTTP_403_FORBIDDEN)
    course = Course.objects.filter(pk=pk).first()
    if not course:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    course.status = 'approved'
    course.rejection_reason = ''
    course.save(update_fields=['status', 'rejection_reason'])
    try:
        if course.instructor_id:
            send_notification(
                sender_id=request.user.id,
                receiver_id=course.instructor_id,
                notification_type='course_update',
                title='Course Approved',
                message=f"Your course '{course.title}' is now live."
            )
    except Exception:
        pass
    return Response({'message': 'Course approved'}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_reject_course(request, pk):
    if request.user.role != 'admin':
        return Response({'error': 'Only admin can reject courses'}, status=status.HTTP_403_FORBIDDEN)
    course = Course.objects.filter(pk=pk).first()
    if not course:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    reason = request.data.get('reason', '')
    course.status = 'rejected'
    course.rejection_reason = reason[:255]
    course.save(update_fields=['status', 'rejection_reason'])
    try:
        if course.instructor_id:
            send_notification(
                sender_id=request.user.id,
                receiver_id=course.instructor_id,
                notification_type='course_update',
                title='Course Rejected',
                message=f"Your course '{course.title}' was rejected. Reason: {course.rejection_reason}"
            )
    except Exception:
        pass
    return Response({'message': 'Course rejected', 'reason': course.rejection_reason}, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_course(request, pk):
    if request.user.role != 'instructor':
        return Response({'error': 'Only instructors can delete courses'}, status=status.HTTP_403_FORBIDDEN)
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    course.delete()
    return Response({'message': 'Course deleted successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_courses(request):
    # Query params
    search = request.query_params.get('search')
    category_ids = request.query_params.getlist('category')
    instructor_name = request.query_params.get('instructor')
    price = request.query_params.get('price')
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    # price_asc, price_desc, enrollments, recent
    order_by = request.query_params.get('order_by')
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 5))
    sort = request.query_params.get('sort')  # e.g., 'top_sellers'
    # Filter for top sellers (by number of enrollments)
    top_sellers = request.query_params.get('top_sellers')
    min_enrollments_param = request.query_params.get('min_enrollments')

    # Base queryset: only approved courses visible to public
    courses = Course.objects.filter(status='approved')

    # Search filter
    if search:
        courses = courses.filter(title__icontains=search)

    # Category filter (support multiple categories)
    if category_ids:
        courses = courses.filter(category__id__in=category_ids)

    # Instructor filter
    if instructor_name:
        search_terms = instructor_name.strip().split()
        instructor_query = Q()
        if len(search_terms) > 1:
            instructor_query |= (
                Q(instructor__first_name__icontains=search_terms[0]) &
                Q(instructor__last_name__icontains=search_terms[-1])
            )
            instructor_query |= (
                Q(instructor__first_name__icontains=search_terms[-1]) &
                Q(instructor__last_name__icontains=search_terms[0])
            )
        else:
            instructor_query |= (
                Q(instructor__first_name__icontains=instructor_name) |
                Q(instructor__last_name__icontains=instructor_name)
            )
        courses = courses.filter(instructor_query)

    # Price filter (exact)
    if price:
        courses = courses.filter(price=price)

    # Price range filter
    if min_price:
        courses = courses.filter(price__gte=min_price)
    if max_price:
        courses = courses.filter(price__lte=max_price)

    # Ordering
    if order_by == 'price_asc':
        courses = courses.order_by('price')
    elif order_by == 'price_desc':
        courses = courses.order_by('-price')
    elif order_by == 'enrollments':
        courses = courses.annotate(enrollments_count=models.Count(
            'enrollments')).order_by('-enrollments_count')
    elif order_by == 'recent':
        courses = courses.order_by('-created_at')

    # Pagination
    total = courses.count()
    start = (page - 1) * limit
    end = start + limit
    courses_page = courses[start:end]

    serializer = CourseSerializer(
        courses_page, many=True, context={'request': request})
    return Response({
        'results': serializer.data,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_course_exam(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        exam = Exam.objects.get(course=course)
    except Exam.DoesNotExist:
        return Response({'error': 'Exam not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ExamSerializer(exam)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_enrollments(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    enrollments = Enrollment.objects.filter(course=course)
    students = [enrollment.student for enrollment in enrollments]
    serializer = UserProfileSerializer(students, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_enrollments(request, student_id):
    enrollments = Enrollment.objects.filter(student__id=student_id)
    courses = [enrollment.course for enrollment in enrollments]
    serializer = CourseSerializer(courses, many=True, context={
                                  'request': request})  # Pass context
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_in_course(request, pk):
    """Enroll authenticated user in a course after Stripe payment."""
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.user.role not in ('student', 'instructor'):
        return Response({'error': 'Only students or instructors can enroll'}, status=status.HTTP_403_FORBIDDEN)
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return Response({'error': 'Already enrolled'}, status=status.HTTP_400_BAD_REQUEST)

    intent_id = request.data.get('intent_id')
    if not intent_id:
        return Response({'error': 'Payment intent ID required'}, status=status.HTTP_400_BAD_REQUEST)

    # Verify payment intent status with Stripe
    try:
        intent = stripe.PaymentIntent.retrieve(intent_id)
        if intent.status != 'succeeded':
            return Response({'error': 'Payment not completed'}, status=status.HTTP_402_PAYMENT_REQUIRED)
    except Exception as e:
        return Response({'error': f'Stripe error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    enrollment = Enrollment.objects.create(student=request.user, course=course)

    # 🔔 Send notification to instructor about new enrollment
    try:
        send_notification(
            sender_id=request.user.id,
            receiver_id=course.instructor.id,
            notification_type='course_enrollment',
            title=f"New Student Enrollment",
            message=f"{request.user.first_name} {request.user.last_name} enrolled in '{course.title}'"
        )
        # Notify user about successful payment and enrollment
        send_notification(
            sender_id=course.instructor.id,
            receiver_id=request.user.id,
            notification_type='payment_success',
            title="Payment Complete",
            message=f"You have successfully paid and enrolled in '{course.title}'."
        )
    except Exception as e:
        print(f"Notification error: {e}")

    return Response({'message': 'Payment complete and enrolled successfully'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_course_completed(request, pk):
    course = Course.objects.filter(pk=pk).first()
    if not course:
        return Response({'error': 'Course not found'}, status=404)
    enrollment = Enrollment.objects.filter(
        student=request.user, course=course).first()
    if not enrollment:
        return Response({'error': 'Not enrolled'}, status=403)
    if enrollment.completed_at:
        return Response({'message': 'Already marked completed'})
    from django.utils import timezone
    enrollment.completed_at = timezone.now()
    enrollment.save(update_fields=['completed_at'])
    try:
        send_notification(
            sender_id=request.user.id,
            receiver_id=course.instructor_id,
            notification_type='course_update',
            title='Course Completed',
            message=f"{request.user.get_full_name() or request.user.email} completed '{course.title}'."
        )
    except Exception:
        pass
    return Response({'message': 'Marked completed'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_from_course(request, pk):
    """Withdraw authenticated user from a course (students and instructors allowed)."""
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.user.role not in ('student', 'instructor'):
        return Response({'error': 'Only students or instructors can withdraw'}, status=status.HTTP_403_FORBIDDEN)
    enrollment = Enrollment.objects.filter(
        student=request.user, course=course).first()
    if not enrollment:
        return Response({'error': 'Not enrolled in this course'}, status=status.HTTP_400_BAD_REQUEST)
    enrollment.delete()
    return Response({'message': 'Withdrawn successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_category(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_course_by_id(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = CourseSerializer(
        course, context={'request': request})  # Pass context
    data = serializer.data
    # include videos
    videos = Video.objects.filter(course=course)
    data['videos'] = VideoSerializer(videos, many=True).data
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


# ========== VIDEO ENDPOINTS ==========

@api_view(['GET'])
@permission_classes([AllowAny])
def list_course_videos(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    videos = Video.objects.filter(course=course)
    return Response(VideoSerializer(videos, many=True).data)


@api_view(['POST'])
@parser_classes([parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser])
@permission_classes([IsAuthenticated])
def create_course_video(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.user.role != 'instructor' or course.instructor_id != request.user.id:
        return Response({'error': 'Only the course instructor can add videos'}, status=status.HTTP_403_FORBIDDEN)
    payload = request.data.copy()
    payload['course'] = course.id
    serializer = VideoSerializer(data=payload)
    if serializer.is_valid():
        try:
            serializer.save(course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@parser_classes([parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser])
@permission_classes([IsAuthenticated])
def update_delete_video(request, video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.user.role != 'instructor' or video.course.instructor_id != request.user.id:
        return Response({'error': 'Only the course instructor can modify videos'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'DELETE':
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = VideoSerializer(video, data=request.data, partial=True)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response(serializer.data)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notify_students(request, pk):
    """Send notification to all enrolled students when instructor makes course updates"""
    try:
        course = Course.objects.get(pk=pk)

        # Check if user is the course instructor
        if course.instructor != request.user:
            return Response({'error': 'Only the course instructor can send notifications'}, status=status.HTTP_403_FORBIDDEN)

        # Get notification data from request
        title = request.data.get('title')
        message = request.data.get('message')
        update_type = request.data.get('update_type', 'course_update')

        if not title or not message:
            return Response({'error': 'Title and message are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get all enrolled students
        enrollments = Enrollment.objects.filter(course=course)
        student_count = 0

        # Send notification to each enrolled student
        for enrollment in enrollments:
            send_notification(
                user_id=enrollment.student.id,
                notification_type='course_update',
                title=title,
                message=message,
                data={
                    'course_id': course.id,
                    'course_title': course.title,
                    'instructor_name': course.instructor.get_full_name(),
                    'update_type': update_type
                }
            )
            student_count += 1

        return Response({
            'message': f'Notification sent to {student_count} enrolled students',
            'student_count': student_count,
            'course_title': course.title
        }, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Failed to send notifications: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- REVIEWS ---


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, course_id):
    course = Course.objects.filter(pk=course_id).first()
    if not course:
        return Response({'error': 'Course not found'}, status=404)
    if not is_enrolled(request.user, course):
        return Response({'error': 'You must be enrolled to review'}, status=403)
    if CourseReview.objects.filter(course=course, rater=request.user).exists():
        return Response({'error': 'You have already reviewed this course'}, status=400)
    serializer = CourseReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(course=course, rater=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_review(request, review_id):
    review = CourseReview.objects.filter(
        pk=review_id, rater=request.user).first()
    if not review:
        return Response({'error': 'Review not found or not yours'}, status=404)
    serializer = CourseReviewSerializer(
        review, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, review_id):
    review = CourseReview.objects.filter(
        pk=review_id, rater=request.user).first()
    if not review:
        return Response({'error': 'Review not found or not yours'}, status=404)
    review.delete()
    return Response({'message': 'Review deleted'}, status=204)

# --- NOTES ---


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_note(request, course_id):
    course = Course.objects.filter(pk=course_id).first()
    if not course:
        return Response({'error': 'Course not found'}, status=404)
    if not is_enrolled(request.user, course):
        return Response({'error': 'You must be enrolled to add notes'}, status=403)
    serializer = CourseNoteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(course=course, author=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_note(request, note_id):
    note = CourseNote.objects.filter(pk=note_id, author=request.user).first()
    if not note:
        return Response({'error': 'Note not found or not yours'}, status=404)
    serializer = CourseNoteSerializer(note, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_note(request, note_id):
    note = CourseNote.objects.filter(pk=note_id, author=request.user).first()
    if not note:
        return Response({'error': 'Note not found or not yours'}, status=404)
    note.delete()
    return Response({'message': 'Note deleted'}, status=204)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_reviews(request, course_id):
    course = Course.objects.filter(pk=course_id).first()
    if not course:
        return Response({'error': 'Course not found'}, status=404)

    # Pagination params
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 5))

    reviews = CourseReview.objects.filter(course=course)
    total = reviews.count()

    start = (page - 1) * limit
    end = start + limit
    reviews_page = reviews[start:end]

    serializer = CourseReviewSerializer(reviews_page, many=True)
    return Response({
        'results': serializer.data,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_notes(request, course_id):
    course = Course.objects.filter(pk=course_id).first()
    if not course:
        return Response({'error': 'Course not found'}, status=404)

    # Pagination params
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 5))

    notes = CourseNote.objects.filter(course=course)
    total = notes.count()

    start = (page - 1) * limit
    end = start + limit
    notes_page = notes[start:end]

    serializer = CourseNoteSerializer(notes_page, many=True)
    return Response({
        'results': serializer.data,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def recommend_courses(request, course_id):
    """
    Recommend up to 4 courses with the same category as the given course.
    """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    # Get courses with the same category, exclude the current course
    recommended = Course.objects.filter(
        category=course.category).exclude(id=course.id)[:4]
    serializer = CourseSerializer(
        recommended, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_for_user(request):
    """
    Recommend up to 4 courses from categories in user's interests.
    If not enough, fill with most enrolled courses.
    """
    user = request.user
    interest_ids = list(user.interests.values_list('id', flat=True))
    recommended = Course.objects.none()

    if interest_ids:
        recommended = Course.objects.filter(
            category__id__in=interest_ids).distinct()[:4]

    count = recommended.count()
    if count < 4:
        # Fill with most enrolled courses not already recommended
        exclude_ids = recommended.values_list('id', flat=True)
        fill_courses = Course.objects.exclude(id__in=exclude_ids)\
            .annotate(enrollments_count=models.Count('enrollments'))\
            .order_by('-enrollments_count')[:4 - count]
        # Combine QuerySets
        recommended = list(recommended) + list(fill_courses)

    serializer = CourseSerializer(
        recommended, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request, pk):
    """
    Create a Stripe PaymentIntent for a course.
    """
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    amount = int(float(course.price) * 100)  # Stripe expects amount in cents
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            metadata={'course_id': course.id, 'user_id': request.user.id}
        )
        return Response({'client_secret': intent.client_secret, 'intent_id': intent.id})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
