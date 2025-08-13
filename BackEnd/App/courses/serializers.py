from rest_framework import serializers
from .models import Course, Enrollment
from authentication.serializers import UserProfileSerializer

class CourseSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    instructor = UserProfileSerializer(read_only=True)
    student_count = serializers.ReadOnlyField()
    enrollment_count = serializers.ReadOnlyField()
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'image', 'instructor', 'student_count', 'enrollment_count', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Set the instructor to the current user
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserProfileSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    enrolled_at = serializers.ReadOnlyField()
    withdrawn_at = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at', 'withdrawn_at', 'is_active']
