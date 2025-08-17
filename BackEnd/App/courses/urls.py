from django.urls import path
from . import views

urlpatterns = [
    # General course endpoints
    path('', views.get_courses, name='get_courses'),
    path('create/', views.create_course, name='create_course'),
    path('<int:pk>/update/', views.update_course, name='update_course'),
    path('<int:pk>/delete/', views.delete_course, name='delete_course'),
    path('<int:pk>/exam/', views.get_course_exam, name='get_course_exam'),
    path('<int:pk>/enrollments/', views.get_course_enrollments, name='get_course_enrollments'),
    path('student/<int:student_id>/enrollments/', views.get_student_enrollments, name='get_student_enrollments'),
    path('<int:pk>/enroll/', views.enroll_in_course, name='enroll_in_course'),
    path('<int:pk>/withdraw/', views.withdraw_from_course, name='withdraw_from_course'),
    
    # Instructor-specific endpoints
    path('instructor/courses/', views.get_instructor_courses, name='get_instructor_courses'),
    path('instructor/courses/<int:course_id>/students/', views.get_course_students, name='get_course_students'),
    path('instructor/courses/<int:course_id>/withdrawn/', views.get_withdrawn_students, name='get_withdrawn_students'),
    
    # Student-specific endpoints
    path('student/courses/', views.get_student_courses, name='get_student_courses'),
]
