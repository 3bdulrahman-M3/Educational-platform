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
<<<<<<< HEAD
        ('assignment_due', 'Assignment Due'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)  # For additional data
=======
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_notifications',
        null=True,
        blank=True
    )
    recipient = models.ForeignKey(  # ✅ only for backward compatibility
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
>>>>>>> origin/notification
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'notifications'

    def __str__(self):
<<<<<<< HEAD
        return f"{self.notification_type} - {self.recipient.email}"
=======
        return f"{self.notification_type} - {self.receiver.email if self.receiver else 'Unknown'}"

    def save(self, *args, **kwargs):
        if not self.receiver and self.recipient:  # auto-populate
            self.receiver = self.recipient
        super().save(*args, **kwargs)
>>>>>>> origin/notification
