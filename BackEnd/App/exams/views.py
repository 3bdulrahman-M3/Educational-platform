from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Exam, Question, ExamQuestion
from .serializers import ExamSerializer, QuestionSerializer, ExamQuestionSerializer


# ==================== QUESTION VIEWS ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def question_list(request):
    """List all questions or create a new question"""
    if request.method == 'GET':
        user = request.user
        if user.role == 'instructor':
            questions = Question.objects.filter(created_by=user)
        else:
            questions = Question.objects.all()

        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Only instructors can create questions
        if request.user.role != 'instructor':
            return Response(
                {'error': 'Only instructors can create questions'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def question_detail(request, pk):
    """Retrieve, update or delete a question"""
    question = get_object_or_404(Question, pk=pk)

    if request.method == 'GET':
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Only instructors can update questions
        if request.user.role != 'instructor':
            return Response(
                {'error': 'Only instructors can update questions'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Only instructors can delete questions
        if request.user.role != 'instructor':
            return Response(
                {'error': 'Only instructors can delete questions'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def question_by_type(request):
    """Get questions filtered by type"""
    question_type = request.query_params.get('type', '')
    user = request.user

    if user.role == 'instructor':
        questions = Question.objects.filter(
            created_by=user, question_type=question_type)
    else:
        questions = Question.objects.filter(question_type=question_type)

    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def question_search(request):
    """Search questions by text or type"""
    query = request.query_params.get('q', '')
    user = request.user

    if user.role == 'instructor':
        questions = Question.objects.filter(created_by=user).filter(
            Q(text__icontains=query) | Q(question_type__icontains=query)
        )
    else:
        questions = Question.objects.filter(
            Q(text__icontains=query) | Q(question_type__icontains=query)
        )

    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


# ==================== EXAM VIEWS ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def exam_list(request):
    """List all exams or create a new exam"""
    if request.method == 'GET':
        user = request.user
        if user.role == 'instructor':
            exams = Exam.objects.filter(created_by=user)
        else:
            exams = Exam.objects.all()

        serializer = ExamSerializer(exams, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Only instructors can create exams
        if request.user.role != 'instructor':
            return Response(
                {'error': 'Only instructors can create exams'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ExamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def exam_detail(request, pk):
    """Retrieve, update or delete an exam"""
    exam = get_object_or_404(Exam, pk=pk)

    if request.method == 'GET':
        serializer = ExamSerializer(exam)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Only instructors can update exams
        if request.user.role != 'instructor':
            return Response(
                {'error': 'Only instructors can update exams'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ExamSerializer(exam, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Only instructors can delete exams
        if request.user.role != 'instructor':
            return Response(
                {'error': 'Only instructors can delete exams'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        exam.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exam_questions(request, pk):
    """Get all questions for a specific exam"""
    exam = get_object_or_404(Exam, pk=pk)
    questions = exam.questions.all()
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_question_to_exam(request, pk):
    """Add a question to an exam"""
    # Only instructors can add questions to exams
    if request.user.role != 'instructor':
        return Response(
            {'error': 'Only instructors can add questions to exams'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    exam = get_object_or_404(Exam, pk=pk)
    question_id = request.data.get('question_id')
    order = request.data.get('order', 0)

    try:
        question = Question.objects.get(id=question_id)
        ExamQuestion.objects.create(exam=exam, question=question, order=order)
        return Response({'message': 'Question added to exam'}, status=status.HTTP_201_CREATED)
    except Question.DoesNotExist:
        return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_question_from_exam(request, pk):
    """Remove a question from an exam"""
    # Only instructors can remove questions from exams
    if request.user.role != 'instructor':
        return Response(
            {'error': 'Only instructors can remove questions from exams'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    exam = get_object_or_404(Exam, pk=pk)
    question_id = request.data.get('question_id')

    try:
        exam_question = ExamQuestion.objects.get(
            exam=exam, question_id=question_id)
        exam_question.delete()
        return Response({'message': 'Question removed from exam'}, status=status.HTTP_200_OK)
    except ExamQuestion.DoesNotExist:
        return Response({'error': 'Question not found in exam'}, status=status.HTTP_404_NOT_FOUND)


# ==================== EXAM QUESTION VIEWS ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def exam_question_list(request):
    """List all exam-question relationships or create a new one"""
    if request.method == 'GET':
        exam_id = request.query_params.get('exam_id')
        if exam_id:
            exam_questions = ExamQuestion.objects.filter(exam_id=exam_id)
        else:
            exam_questions = ExamQuestion.objects.all()

        serializer = ExamQuestionSerializer(exam_questions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ExamQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def exam_question_detail(request, pk):
    """Retrieve, update or delete an exam-question relationship"""
    exam_question = get_object_or_404(ExamQuestion, pk=pk)

    if request.method == 'GET':
        serializer = ExamQuestionSerializer(exam_question)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ExamQuestionSerializer(exam_question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        exam_question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
