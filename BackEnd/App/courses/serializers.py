from rest_framework import serializers
from .models import Course, Enrollment, Category, Video, CourseReview, CourseNote
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
    enrollments_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'image', 'instructor',
            'instructor_name', 'category', 'category_name', 'is_enrolled',
            'enrollments_count',
            'instructor_name', 'category', 'category_name', 'is_enrolled', 'price'
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

    def get_enrollments_count(self, obj):
        return Enrollment.objects.filter(course=obj).count()

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


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'course', 'title', 'url', 'file', 'description', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'course']

    def validate(self, attrs):
        url = attrs.get('url')
        file = attrs.get('file')
        if not url and not file:
            raise serializers.ValidationError('Either a URL or a file must be provided for the video.')
        return attrs

class CourseReviewSerializer(serializers.ModelSerializer):
    rater_first_name = serializers.CharField(source='rater.first_name', read_only=True)
    rater_last_name = serializers.CharField(source='rater.last_name', read_only=True)

    class Meta:
        model = CourseReview
        fields = ['id', 'course', 'content', 'rating', 'rater', 'rater_first_name', 'rater_last_name', 'posted_at', 'updated_at']
        read_only_fields = ['rater', 'posted_at', 'updated_at', 'rater_first_name', 'rater_last_name','course']

class CourseNoteSerializer(serializers.ModelSerializer):
    author_first_name = serializers.CharField(source='author.first_name', read_only=True)
    author_last_name = serializers.CharField(source='author.last_name', read_only=True)

    class Meta:
        model = CourseNote
        fields = ['id', 'course', 'content', 'author', 'author_first_name', 'author_last_name', 'posted_at', 'updated_at']
        read_only_fields = ['author','course', 'posted_at', 'updated_at', 'author_first_name', 'author_last_name']