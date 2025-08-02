from django.contrib import admin
from .models import Exam, Question, ExamQuestion


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question_type',
                    'points', 'created_by', 'created_at']
    list_filter = ['question_type', 'created_at']
    search_fields = ['text']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'question_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ['exam', 'question', 'order']
    list_filter = ['exam']
    ordering = ['exam', 'order']
