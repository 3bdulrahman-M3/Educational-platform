from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Exam, Question
from .serializers import (
    ExamSerializer, QuestionCreateSerializer
)


# ==================== QUESTION VIEWS ====================


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def question_list(request):
    if request.user.role != 'instructor':
        return Response(
            {'error': 'Only instructors can create questions'},
            status=status.HTTP_403_FORBIDDEN
        )
    serializer = QuestionCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def question_detail(request, pk):
    """update or delete a question"""
    question = get_object_or_404(Question, pk=pk)

    if request.method == 'PUT':
        # Only instructors can update questions
        if request.user.role != 'instructor':
            return Response(
                {'error': 'Only instructors can update questions'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = QuestionCreateSerializer(question, data=request.data)
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
        return Response(
            {'message': 'Question deleted successfully'},
            status=status.HTTP_200_OK)


# ==================== EXAM VIEWS ====================


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def exam_list(request):
    """List all exams, get exam by ID, create a new exam, update or delete an exam"""
    if request.method == 'GET':
        exam_id = request.query_params.get('exam_id')
        
        if exam_id:
            # Get specific exam by ID
            exam = get_object_or_404(Exam, pk=exam_id)
            serializer = ExamSerializer(exam)
            return Response(serializer.data)
        else:
            # Get all exams
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

    elif request.method == 'PUT':
        # Only instructors can update exams
        if request.user.role != 'instructor':
            return Response(
                {'error': 'Only instructors can update exams'},
                status=status.HTTP_403_FORBIDDEN
            )
        exam_id = request.data.get('id')
        if not exam_id:
            return Response(
                {'error': 'Exam ID is required for update'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exam = get_object_or_404(Exam, pk=exam_id)
        
        # Extract questions data from request
        questions_data = request.data.pop('questions', None)
        
        # Update exam basic info
        serializer = ExamSerializer(exam, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Handle questions updates only if questions_data is provided
            if questions_data is not None:
                # Process questions from request
                for question_data in questions_data:
                    question_id = question_data.get('id')
                    
                    if question_id:
                        # Update existing question
                        try:
                            question = Question.objects.get(
                                id=question_id, exam=exam
                            )
                            question_serializer = QuestionCreateSerializer(
                                question, data=question_data, partial=True
                            )
                            if question_serializer.is_valid():
                                question_serializer.save()
                            else:
                                return Response(
                                    {
                                        'error': f'Invalid question data: '
                                        f'{question_serializer.errors}'
                                    },
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                        except Question.DoesNotExist:
                            return Response(
                                {
                                    'error': f'Question with ID {question_id} '
                                    f'not found in this exam'
                                },
                                status=status.HTTP_404_NOT_FOUND
                            )
                    else:
                        # Create new question
                        question_data['exam'] = exam_id
                        question_serializer = QuestionCreateSerializer(
                            data=question_data
                        )
                        if question_serializer.is_valid():
                            question_serializer.save(created_by=request.user)
                        else:
                            return Response(
                                {
                                    'error': f'Invalid new question data: '
                                    f'{question_serializer.errors}'
                                },
                                status=status.HTTP_400_BAD_REQUEST
                            )
            
            # Return updated exam with questions
            updated_exam = Exam.objects.get(pk=exam_id)
            response_serializer = ExamSerializer(updated_exam)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Only instructors can delete exams
        if request.user.role != 'instructor':
            return Response(
                {'error': 'Only instructors can delete exams'},
                status=status.HTTP_403_FORBIDDEN
            )
        exam_id = request.data.get('id')
        if not exam_id:
            return Response(
                {'error': 'Exam ID is required for deletion'},
                status=status.HTTP_400_BAD_REQUEST
            )
        exam = get_object_or_404(Exam, pk=exam_id)
        exam.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
