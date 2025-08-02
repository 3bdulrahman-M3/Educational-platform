from django.db import models
from authentication.models import User


class Question(models.Model):
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('essay', 'Essay'),
        ('short_answer', 'Short Answer'),
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


class Exam(models.Model):
    name = models.CharField(max_length=255)
    questions = models.ManyToManyField(Question, through='ExamQuestion')
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_exams',
        limit_choices_to={'role': 'instructor'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'exams'
        ordering = ['-created_at']


class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'exam_questions'
        ordering = ['order']
        unique_together = ['exam', 'question']
