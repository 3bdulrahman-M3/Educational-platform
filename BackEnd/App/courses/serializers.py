from rest_framework import serializers
from .models import Course, Enrollment
from authentication.serializers import UserProfileSerializer

class CourseSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'image']

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserProfileSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at']