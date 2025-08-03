from rest_framework import serializers
from .models import Exam, Question, ExamQuestion, Choice
from authentication.serializers import UserProfileSerializer


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer(read_only=True)
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'points',
                  'created_by', 'created_at', 'updated_at', 'choices']
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class QuestionCreateSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)
    created_by = UserProfileSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'points',
                  'created_by', 'created_at', 'updated_at', 'choices']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def _is_true_false_question(self, text):
        """Check if the question is asking for True/False answer"""
        true_false_indicators = [
            "is this the answer is either true or false?",
            "is the answer true or false?",
            "is this true or false?",
            "true or false?",
            "is it true or false?",
            "is this statement true or false?",
            "is the following true or false?",
            "is this correct true or false?",
            "is this the answer true or false?",
            "is this either true or false?",
            "is this answer true or false?",
            "is this the correct answer true or false?",
            "is this the right answer true or false?",
            "is this the solution true or false?",
            "is this the case true or false?",
            "is this the result true or false?",
            "is this the outcome true or false?",
            "is this the conclusion true or false?",
            "is this the finding true or false?",
            "is this the observation true or false?"
        ]
        
        question_lower = text.lower().strip()
        return any(indicator in question_lower for indicator in true_false_indicators)

    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        question = Question.objects.create(**validated_data)
        
        # Check if it's a True/False question
        if self._is_true_false_question(question.text):
            # Create default True/False choices
            Choice.objects.create(
                question=question,
                text="True",
                is_correct=True,
                order=1
            )
            Choice.objects.create(
                question=question,
                text="False",
                is_correct=False,
                order=2
            )
        elif not choices_data:
            # If no choices provided and not True/False, create default True/False
            Choice.objects.create(
                question=question,
                text="True",
                is_correct=True,
                order=1
            )
            Choice.objects.create(
                question=question,
                text="False",
                is_correct=False,
                order=2
            )
        else:
            # Create custom choices
            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)
        
        return question

    def update(self, instance, validated_data):
        choices_data = validated_data.pop('choices', [])
        instance = super().update(instance, validated_data)
        
        # Update choices
        if choices_data or self._is_true_false_question(instance.text):
            # Delete existing choices
            instance.choices.all().delete()
            
            # Check if it's a True/False question
            if self._is_true_false_question(instance.text):
                # Create default True/False choices
                Choice.objects.create(
                    question=instance,
                    text="True",
                    is_correct=True,
                    order=1
                )
                Choice.objects.create(
                    question=instance,
                    text="False",
                    is_correct=False,
                    order=2
                )
            else:
                # Create custom choices
                for choice_data in choices_data:
                    Choice.objects.create(question=instance, **choice_data)
        
        return instance


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
