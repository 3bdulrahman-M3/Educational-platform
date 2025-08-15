from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Session(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    max_participants = models.IntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(20)]
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_sessions'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.creator.get_full_name()}"

    @property
    def is_full(self):
        """Check if session is at maximum capacity"""
        return self.participants.count() >= self.max_participants

    @property
    def available_spots(self):
        """Get number of available spots"""
        return max(0, self.max_participants - self.participants.count())

    @property
    def is_upcoming(self):
        """Check if session is upcoming"""
        return self.status == 'upcoming' and self.date > timezone.now()

    @property
    def is_ongoing(self):
        """Check if session is currently ongoing"""
        return self.status == 'ongoing'

    @property
    def is_completed(self):
        """Check if session is completed"""
        return self.status == 'completed'

    @property
    def is_cancelled(self):
        """Check if session is cancelled"""
        return self.status == 'cancelled'

    @property
    def can_join(self):
        """Check if session can be joined"""
        return self.is_upcoming and not self.is_full and not self.is_cancelled

    def can_be_cancelled_by(self, user):
        """Check if user can cancel this session"""
        return self.creator == user and self.status in ['upcoming', 'ongoing']


class Participant(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
    ]

    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='session_participations'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['session', 'user']
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user.get_full_name()} in {self.session.title}"

    @property
    def is_tutor(self):
        """Check if participant is a tutor"""
        return self.role == 'tutor'

    @property
    def is_student(self):
        """Check if participant is a student"""
        return self.role == 'student'
