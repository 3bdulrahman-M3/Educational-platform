from django.db import models
from authentication.models import User

class LiveSession(models.Model):
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    created_at = models.DateTimeField(auto_now_add=True)
    room_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title
