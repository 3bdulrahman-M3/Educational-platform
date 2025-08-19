from rest_framework import serializers
from .models import Course, Enrollment, Category
from authentication.serializers import UserProfileSerializer
from authentication.models import User

class CourseSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, required=False, allow_null=True
    )
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    instructor_name = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'image', 'instructor',
            'instructor_name', 'category', 'category_name', 'is_enrolled'
        ]

    def get_is_enrolled(self, obj):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return Enrollment.objects.filter(course=obj, student=request.user).exists()
        return False

    def get_instructor_name(self, obj):
        if obj.instructor:
            first = obj.instructor.first_name or ""
            last = obj.instructor.last_name or ""
            return f"{first} {last}".strip()
        return ""

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserProfileSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image_url']


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'role'
        )