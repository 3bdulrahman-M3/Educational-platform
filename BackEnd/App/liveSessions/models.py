from django.db import models
from authentication.models import User
from django.utils import timezone
from datetime import timedelta


def default_end_date():
    return timezone.now() + timedelta(days=1)


class LiveSessionManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs.filter(end_date__lt=timezone.now()).delete()
        return qs
    

class LiveSession(models.Model):
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    created_at = models.DateTimeField(auto_now_add=True)
    room_name = models.CharField(max_length=255, unique=True)
    end_date = models.DateTimeField(default=default_end_date)  # ✅ Default = now + 1 day

    objects = LiveSessionManager()

    def __str__(self):
        return self.title

    def is_expired(self):
        return self.end_date and timezone.now() >= self.end_date
