from rest_framework import serializers
from .models import Exam, Question, ExamQuestion
from authentication.serializers import UserProfileSerializer


class QuestionSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'points',
                  'created_by', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class ExamQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = ExamQuestion
        fields = ['id', 'exam', 'question', 'order']


class ExamSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'name', 'created_by', 'questions',
                  'question_count', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_question_count(self, obj):
        return obj.questions.count()


class ExamDetailSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'name', 'created_by',
                  'questions', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']
