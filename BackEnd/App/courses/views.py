from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated,  AllowAny
from rest_framework.response import Response
from rest_framework import status, parsers, generics
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
        course = serializer.save(instructor=request.user)

        # 🔔 Send notification to all students about new course
        try:
            students = User.objects.filter(role='student')
            for student in students:
                send_notification(
                    sender_id=request.user.id,
                    receiver_id=student.id,
                    notification_type='course_created',
                    title=f"New Course Available",
                    message=f"New course '{course.title}' is now available!"
                )
        except Exception as e:
            print(f"Notification error: {e}")

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
        course = serializer.save()

        # 🔔 Send notification to all enrolled students about course update
        try:
            enrolled_students = User.objects.filter(
                enrollments__course=course
            ).distinct()
            for student in enrolled_students:
                send_notification(
                    sender_id=request.user.id,
                    receiver_id=student.id,
                    notification_type='course_updated',
                    title=f"Course Updated",
                    message=f"Course '{course.title}' has been updated!"
                )
        except Exception as e:
            print(f"Notification error: {e}")

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
    category_ids = request.query_params.getlist(
        'category')  # e.g. ?category=1&category=2
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 5))

    # Base queryset
    courses = Course.objects.all()

    # Search filter
    if search:
        courses = courses.filter(title__icontains=search)

    # Category filter (support multiple categories)
    if category_ids:
        courses = courses.filter(category__id__in=category_ids)

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
    except Exception as e:
        print(f"Notification error: {e}")

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
