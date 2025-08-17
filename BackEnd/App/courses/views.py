from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, parsers
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from exams.serializers import ExamSerializer
from exams.models import Exam
from authentication.serializers import UserProfileSerializer
from django.utils import timezone

# Create your views here.

@api_view(['POST'])
@parser_classes([parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser])
@permission_classes([IsAuthenticated])
def create_course(request):
    if request.user.role != 'instructor':
        return Response({'error': 'Only instructors can create courses'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CourseSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@parser_classes([parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser])
@permission_classes([IsAuthenticated])
def update_course(request, pk):
    if request.user.role != 'instructor':
        return Response({'error': 'Only instructors can update courses'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        course = Course.objects.get(pk=pk, instructor=request.user)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CourseSerializer(course, data=request.data, partial=True, context={'request': request})
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
        course = Course.objects.get(pk=pk, instructor=request.user)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    course.delete()
    return Response({'message': 'Course deleted successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_courses(request):
    course_id = request.query_params.get('id')
    if course_id:
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    else:
        # Get newest courses first
        courses = Course.objects.all().order_by('-created_at')
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

# Instructor-specific endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_instructor_courses(request):
    """Get all courses created by the instructor."""
    if request.user.role != 'instructor':
        return Response({'error': 'Only instructors can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    courses = Course.objects.filter(instructor=request.user).order_by('-created_at')
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_students(request, course_id):
    """Get all students enrolled in a specific course (for instructor)."""
    if request.user.role != 'instructor':
        return Response({'error': 'Only instructors can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        course = Course.objects.get(pk=course_id, instructor=request.user)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get active enrollments (not withdrawn)
    enrollments = Enrollment.objects.filter(course=course, withdrawn_at__isnull=True)
    serializer = EnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_withdrawn_students(request, course_id):
    """Get all students who withdrew from a specific course (for instructor)."""
    if request.user.role != 'instructor':
        return Response({'error': 'Only instructors can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        course = Course.objects.get(pk=course_id, instructor=request.user)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get withdrawn enrollments
    enrollments = Enrollment.objects.filter(course=course, withdrawn_at__isnull=False)
    serializer = EnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)

# Student-specific endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_courses(request):
    """Get all courses the student is enrolled in."""
    if request.user.role != 'student':
        return Response({'error': 'Only students can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    enrollments = Enrollment.objects.filter(student=request.user).order_by('-enrolled_at')
    serializer = EnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_in_course(request, pk):
    """Student enrolls (or re-enrolls) in a course."""
    if request.user.role != 'student':
        return Response({'error': 'Only students can enroll'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        enrollment = Enrollment.objects.get(student=request.user, course=course)
        if enrollment.withdrawn_at is None:
            return Response({'error': 'Already enrolled in this course'}, status=status.HTTP_400_BAD_REQUEST)
        # Re-enroll: reset withdrawn_at and update enrolled_at
        enrollment.withdrawn_at = None
        enrollment.enrolled_at = timezone.now()
        enrollment.save()
    except Enrollment.DoesNotExist:
        enrollment = Enrollment.objects.create(student=request.user, course=course)
    
    serializer = EnrollmentSerializer(enrollment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_from_course(request, pk):
    """Student withdraws from a course."""
    if request.user.role != 'student':
        return Response({'error': 'Only students can withdraw'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        enrollment = Enrollment.objects.get(student=request.user, course=course, withdrawn_at__isnull=True)
    except Enrollment.DoesNotExist:
        return Response({'error': 'Not enrolled in this course or already withdrawn'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Mark as withdrawn
    enrollment.withdraw()
    return Response({'message': 'Successfully withdrawn from course'}, status=status.HTTP_200_OK)

# Existing endpoints (keep for compatibility)
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
    enrollments = Enrollment.objects.filter(student__id=student_id, withdrawn_at__isnull=True)
    courses = [enrollment.course for enrollment in enrollments]
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)
