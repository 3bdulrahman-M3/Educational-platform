from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_courses',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)

    def __str__(self):
        return self.title

    @property
    def student_count(self):
        """Return the number of active students enrolled in this course."""
        return self.enrollments.filter(withdrawn_at__isnull=True).count()

    @property
    def enrollment_count(self):
        """Return the total number of enrollments (including withdrawn)."""
        return self.enrollments.count()

class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.email} enrolled in {self.course.title}"

    def withdraw(self):
        """Mark enrollment as withdrawn."""
        from django.utils import timezone
        self.withdrawn_at = timezone.now()
        self.is_active = False
        self.save()
