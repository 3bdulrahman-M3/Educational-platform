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
from django.db.models import Q, Count
from decimal import Decimal, InvalidOperation
from notifications.views import send_notification

# Create your views here.


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
        serializer.save(instructor=request.user)
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
    serializer = CourseSerializer(course, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    category_ids = request.query_params.getlist(
        'category')  # e.g. ?category=1&category=2
    instructor_name = request.query_params.get('instructor')  
    price = request.query_params.get('price')
    price_min = request.query_params.get('price_min') or request.query_params.get('min_price')
    price_max = request.query_params.get('price_max') or request.query_params.get('max_price')
    price_range = request.query_params.get('price_range')  # accepts formats like "10-50" or "10,50"
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 5))
    sort = request.query_params.get('sort')  # e.g., 'top_sellers'
    # Filter for top sellers (by number of enrollments)
    top_sellers = request.query_params.get('top_sellers')
    min_enrollments_param = request.query_params.get('min_enrollments')

    # Base queryset
    courses = Course.objects.all()

    # Search filter
    if search:
        courses = courses.filter(title__icontains=search)

    # Category filter (support multiple categories)
    if category_ids:
        courses = courses.filter(category__id__in=category_ids)

    if instructor_name:
        # Split the search term into parts for more flexible matching
        search_terms = instructor_name.strip().split()
        
        # Build a more comprehensive search query
        instructor_query = Q()
        
        # If multiple terms, search for exact first+last name combination
        if len(search_terms) > 1:
            # Search for first name + last name combination
            instructor_query |= (
                Q(instructor__first_name__icontains=search_terms[0]) & 
                Q(instructor__last_name__icontains=search_terms[-1])
            )
            # Also search for last name + first name combination
            instructor_query |= (
                Q(instructor__first_name__icontains=search_terms[-1]) & 
                Q(instructor__last_name__icontains=search_terms[0])
            )
        else:
            # Single term - search in both first and last name
            instructor_query |= (
                Q(instructor__first_name__icontains=instructor_name) |
                Q(instructor__last_name__icontains=instructor_name)
            )
        
        courses = courses.filter(instructor_query)
    # Price filter
    # Backwards compatible exact price match
    if price and not (price_min or price_max or price_range):
        try:
            courses = courses.filter(price=Decimal(price))
        except (InvalidOperation, TypeError):
            pass

    # Range-based price filtering
    min_value = None
    max_value = None

    # Parse price_range if provided (e.g., "10-50" or "10,50")
    if price_range and not (price_min or price_max):
        separator = '-' if '-' in price_range else ',' if ',' in price_range else None
        if separator:
            parts = [p.strip() for p in price_range.split(separator, 1)]
            if parts and parts[0] != '':
                try:
                    min_value = Decimal(parts[0])
                except InvalidOperation:
                    min_value = None
            if len(parts) > 1 and parts[1] != '':
                try:
                    max_value = Decimal(parts[1])
                except InvalidOperation:
                    max_value = None

    # Parse explicit min/max if provided
    if price_min:
        try:
            min_value = Decimal(price_min)
        except InvalidOperation:
            min_value = None
    if price_max:
        try:
            max_value = Decimal(price_max)
        except InvalidOperation:
            max_value = None

    if min_value is not None:
        courses = courses.filter(price__gte=min_value)
    if max_value is not None:
        courses = courses.filter(price__lte=max_value)
    # Top sellers filter (enrollments > 0 by default, or >= min_enrollments)
    if top_sellers in ('1', 'true', 'True', 'yes', 'on') or (min_enrollments_param is not None):
        try:
            min_enrollments = int(min_enrollments_param) if min_enrollments_param is not None else 1
        except (TypeError, ValueError):
            min_enrollments = 1
        courses = courses.annotate(num_enrollments=Count('enrollments')).filter(num_enrollments__gte=min_enrollments)

    # Sorting
    if sort == 'top_sellers':
        # Order by number of enrollments descending
        if 'num_enrollments' in [a.name for a in courses.query.annotations.values()]:
            courses = courses.order_by('-num_enrollments', '-id')
        else:
            courses = courses.annotate(num_enrollments=Count('enrollments')).order_by('-num_enrollments', '-id')

    # Pagination
    total = courses.count()
    start = (page - 1) * limit
    end = start + limit
    courses_page = courses[start:end]

    serializer = CourseSerializer(courses_page, many=True, context={
                                  'request': request})  # Pass context
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
    """Enroll authenticated user in a course (students and instructors allowed)."""
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.user.role not in ('student', 'instructor'):
        return Response({'error': 'Only students or instructors can enroll'}, status=status.HTTP_403_FORBIDDEN)
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return Response({'error': 'Already enrolled'}, status=status.HTTP_400_BAD_REQUEST)
    Enrollment.objects.create(student=request.user, course=course)
    return Response({'message': 'Enrolled successfully'}, status=status.HTTP_201_CREATED)


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
