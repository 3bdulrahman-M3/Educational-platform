from django.urls import path
from . import views

urlpatterns = [
    # ==================== QUESTION URLS ====================
    path('questions/', views.question_list, name='question_list'),
    path('questions/<int:pk>/', views.question_detail, name='question_detail'),

    # ==================== EXAM URLS ====================
    path('exams/', views.exam_list, name='exam_list'),
]
