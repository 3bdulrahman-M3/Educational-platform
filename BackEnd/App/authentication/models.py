from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField
from courses.models import Category  # Add this import at the top


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )

    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='student')
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    bio = models.TextField(
        blank=True, default='This user prefers to keep an air of mystery about them.')
    image = CloudinaryField(
        'image',
        blank=True,
        null=True,
        default='https://res.cloudinary.com/ddtp8tqvv/image/upload/v1756197579/teenage-girl-with-headphones-laptop-online-school_lxptu5.jpg'
    )
    interests = models.ManyToManyField(
        Category, related_name='interested_users', blank=True)  # Added field

    # Identity verification status
    VERIFIED_CHOICES = (
        ('not_verified', 'Not Verified'),
        ('pending', 'Pending'),
        ('verified', 'Verified'),
    )
    verified = models.CharField(
        max_length=20, choices=VERIFIED_CHOICES, default='not_verified'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'auth_user'


class InstructorRequest(models.Model):
    user = models.OneToOneField(
        'User', on_delete=models.CASCADE, related_name='instructor_request')
    motivation = models.TextField(blank=True)
    # Extra applicant details
    full_name = models.CharField(max_length=150, blank=True)
    degree = models.CharField(max_length=150, blank=True)
    certifications = models.TextField(blank=True)
    # Primary profile document/photo (Cloudinary secure URL)
    photo_url = models.URLField(blank=True)
    # Store uploaded document URLs (e.g., Cloudinary URLs)
    documents = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ), default='pending')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        'User', null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_instructor_requests')

    class Meta:
        db_table = 'instructor_requests'
        ordering = ['-created_at']


class IdentityVerificationRequest(models.Model):
    """Stores a user's identity verification request and uploaded ID photo."""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.OneToOneField(
        'User', on_delete=models.CASCADE, related_name='identity_verification_request'
    )
    # Primary ID photo (Cloudinary or storage URL)
    id_photo_url = models.URLField(blank=True)
    # Optional metadata
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        'User', null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_identity_requests'
    )

    class Meta:
        db_table = 'identity_verification_requests'
        ordering = ['-created_at']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = CloudinaryField(
        'image',
        blank=True,
        null=True,
        default='https://www.gravatar.com/avatar/?d=mp'
    )
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.email}"

    class Meta:
        db_table = 'user_profile'


class PasswordResetToken(models.Model):
    """Single-use password reset token with expiration."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"PasswordResetToken(user={self.user.email}, used={self.is_used})"

    class Meta:
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]
