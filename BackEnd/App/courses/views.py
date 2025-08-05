from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status,parsers
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from exams.serializers import ExamSerializer
from exams.models import Exam
from authentication.serializers import UserProfileSerializer

# Create your views here.

@api_view(['POST'])# @parser_classes([parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser])
@permission_classes([IsAuthenticated])
def create_course(request):
    if request.user.role != 'instructor':
        return Response({'error': 'Only instructors can create courses'}, status=status.HTTP_403_FORBIDDEN)
    serializer = CourseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])# @parser_classes([parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser])
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
    course_id = request.query_params.get('id')
    if course_id:
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    else:
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

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
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_in_course(request, pk):
    """Student enrolls in a course."""
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.user.role != 'student':
        return Response({'error': 'Only students can enroll'}, status=status.HTTP_403_FORBIDDEN)
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return Response({'error': 'Already enrolled'}, status=status.HTTP_400_BAD_REQUEST)
    Enrollment.objects.create(student=request.user, course=course)
    return Response({'message': 'Enrolled successfully'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_from_course(request, pk):
    """Student withdraws from a course."""
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.user.role != 'student':
        return Response({'error': 'Only students can withdraw'}, status=status.HTTP_403_FORBIDDEN)
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    if not enrollment:
        return Response({'error': 'Not enrolled in this course'}, status=status.HTTP_400_BAD_REQUEST)
    enrollment.delete()
    return Response({'message': 'Withdrawn successfully'}, status=status.HTTP_200_OK)
