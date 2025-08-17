from django.db import models
from authentication.models import User
from courses.models import Course


class Exam(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_exams',
        limit_choices_to={'role': 'instructor'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='exam', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'exams'
        ordering = ['-created_at']


class Question(models.Model):
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'), 
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions',
        null=True,  # Allow null for migration safety, can remove later
        blank=True
    )
    text = models.TextField()
    question_type = models.CharField(
        max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    points = models.IntegerField(default=1)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_questions',
        limit_choices_to={'role': 'instructor'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.text[:50]}..."

    class Meta:
        db_table = 'questions'
        ordering = ['-created_at']


class Choice(models.Model):
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='choices'
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.question.text[:30]} - {self.text}"

    class Meta:
        db_table = 'choices'
        ordering = ['order']
        unique_together = ['question', 'order']
