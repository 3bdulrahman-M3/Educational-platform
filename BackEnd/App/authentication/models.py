from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    ROLE_CHOICES = (
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    bio = models.TextField(blank=True, default='This user prefers to keep an air of mystery about them.')
    image = CloudinaryField(
        'image',
        blank=True,
        null=True,
        default='https://res.cloudinary.com/ddtp8tqvv/image/upload/v1756197579/teenage-girl-with-headphones-laptop-online-school_lxptu5.jpg'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    def __str__(self):
        return self.email
    
    class Meta:
        db_table = 'auth_user'


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