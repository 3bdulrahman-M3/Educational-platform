from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Session(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    STATUS_CHOICES = [
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.CharField(max_length=100, default='General')
    level = models.CharField(
        max_length=20, choices=LEVEL_CHOICES, default='beginner')
    date = models.DateTimeField()  # Store in UTC
    duration = models.IntegerField(help_text="Duration in minutes", default=60)
    max_participants = models.IntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(50)]
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_sessions'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_approval'
    )
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Live session specific fields
    room_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True)
    recording_enabled = models.BooleanField(default=False)
    chat_enabled = models.BooleanField(default=True)
    screen_sharing_enabled = models.BooleanField(default=True)

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
    def is_full(self):
        return self.participants.filter(status='approved').count() >= self.max_participants

    @property
    def available_spots(self):
        return max(0, self.max_participants - self.participants.filter(status='approved').count())

    @property
    def participant_count(self):
        return self.participants.filter(status='approved').count()

    @property
    def is_upcoming(self):
        """Check if session is upcoming"""
        return self.status in ['approved', 'scheduled'] and self.date > timezone.now()

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
        return self.status in ['scheduled', 'approved'] and not self.is_full and not self.is_cancelled

    def can_be_cancelled_by(self, user):
        """Check if user can cancel this session"""
        return self.creator == user and self.status in ['pending_approval', 'approved', 'scheduled', 'ongoing']

    def generate_room_id(self):
        """Generate a unique room ID for WebRTC"""
        import uuid
        if not self.room_id:
            self.room_id = f"session_{self.id}_{uuid.uuid4().hex[:8]}"
            self.save(update_fields=['room_id'])
        return self.room_id


class Participant(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

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
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
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


class LiveParticipantState(models.Model):
    """Track real-time participant states during live sessions"""
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='live_participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='live_session_states'
    )
    is_connected = models.BooleanField(default=False)
    audio_enabled = models.BooleanField(default=False)
    video_enabled = models.BooleanField(default=False)
    screen_sharing = models.BooleanField(default=False)
    hand_raised = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    connection_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ['session', 'user']
        ordering = ['-last_seen']

    def __str__(self):
        return f"{self.user.get_full_name()} in {self.session.title}"


class SessionMessage(models.Model):
    """Chat messages during live sessions"""
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='session_messages'
    )
    message = models.TextField()
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('chat', 'Chat'),
            ('system', 'System'),
            ('notification', 'Notification'),
        ],
        default='chat'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.message[:50]}"


class SessionRecording(models.Model):
    """Session recordings"""
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='recordings'
    )
    recording_url = models.URLField()
    duration = models.IntegerField(
        help_text="Duration in seconds", null=True, blank=True)
    file_size = models.BigIntegerField(
        help_text="File size in bytes", null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='session_recordings'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Recording for {self.session.title}"


class BookingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='booking_requests'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['session', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} request for {self.session.title}"


class SessionMaterial(models.Model):
    TYPE_CHOICES = [
        ('file', 'File'),
        ('link', 'Link'),
        ('note', 'Note'),
    ]

    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='materials'
    )
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    url = models.URLField(blank=True)
    file = models.FileField(upload_to='session_materials/', blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} for {self.session.title}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('reminder', 'Reminder'),
        ('booking_request', 'Booking Request'),
        ('session_update', 'Session Update'),
        ('general', 'General'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} for {self.user.get_full_name()}"
