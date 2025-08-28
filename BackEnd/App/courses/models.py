from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=3, default=0.00, db_column='Price')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_courses',
        null=True,
        blank=True
    )  # Added creator field
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True,
        help_text="Duration in hours (e.g., 1.50 = 1 hour 30 mins)"
    )
    level = models.CharField(max_length=50, blank=True, null=True, default='Beginner')
    language = models.CharField(max_length=50, blank=True, null=True, default='English')
    learning_objectives = models.JSONField(default=list, blank=True)
    requirements = models.JSONField(default=list, blank=True)
    target_audience = models.JSONField(default=list, blank=True)


    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.email} enrolled in {self.course.title}"


class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    # Optional direct URL if instructor wants to link from YouTube/Vimeo/etc.
    url = models.URLField(max_length=1000, blank=True, null=True)
    # Optional uploaded video file via Cloudinary
    file = CloudinaryField('video', resource_type='video', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.title} ({self.course.title})"
    

class CourseReview(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_reviews')
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'rater')

    def __str__(self):
        return f"Review by {self.rater.email} on {self.course.title}"

class CourseNote(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_notes')
    content = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note by {self.author.email} on {self.course.title}"