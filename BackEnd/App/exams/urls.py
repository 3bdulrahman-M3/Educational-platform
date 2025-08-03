from django.urls import path
from . import views

urlpatterns = [
    # ==================== QUESTION URLS ====================
    path('questions/', views.question_list, name='question_list'),
    path('questions/<int:pk>/', views.question_detail, name='question_detail'),

    # ==================== EXAM URLS ====================
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/<int:pk>/', views.exam_detail, name='exam_detail'),
    path('exams/<int:pk>/questions/', views.exam_questions, name='exam_questions'),
    path('exams/<int:pk>/add_question/',
         views.add_question_to_exam, name='add_question_to_exam'),
    path('exams/<int:pk>/remove_question/',
         views.remove_question_from_exam, name='remove_question_from_exam'),

    # ==================== EXAM QUESTION URLS ====================
    path('exam-questions/', views.exam_question_list, name='exam_question_list'),
    path('exam-questions/<int:pk>/', views.exam_question_detail,
         name='exam_question_detail'),
]
