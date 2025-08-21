from django.db import models
from django.conf import settings


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('course_enrollment', 'Course Enrollment'),
        ('session_start', 'Live Session Start'),
        ('exam_result', 'Exam Result'),
        ('message', 'Message'),
        ('announcement', 'Announcement'),
        ('course_update', 'Course Update'),
        ('assignment_due', 'Assignment Due'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)  # For additional data
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'notifications'

    def __str__(self):
        return f"{self.notification_type} - {self.recipient.email}"
