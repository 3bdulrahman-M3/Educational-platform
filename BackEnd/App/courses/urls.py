from django.urls import path
from . import views

urlpatterns = [
    # Courses
    path('', views.get_courses, name='get_courses'),
    path('<int:pk>/', views.get_course_by_id, name='get_course_by_id'),
    path('create/', views.create_course, name='create_course'),
    path('<int:pk>/update/', views.update_course, name='update_course'),
    path('<int:pk>/delete/', views.delete_course, name='delete_course'),
    path('instructors/', views.get_instructors, name='get_instructors'),
    path('categories/', views.get_all_categories, name='get_all_categories'),
    path('<int:pk>/enroll/', views.enroll_in_course, name='enroll_in_course'),
    path('<int:pk>/withdraw/', views.withdraw_from_course,
         name='withdraw_from_course'),
    path('student/<int:student_id>/enrollments/',
         views.get_student_enrollments, name='get_student_enrollments'),
    path('instructor/<int:instructor_id>/courses/',
         views.get_instructor_with_courses, name='get_instructor_with_courses'),
    path('<int:pk>/notify-students/',
         views.notify_students, name='notify_students'),

    # Reviews

    path('<int:course_id>/reviews/list/', views.get_course_reviews, name='get_course_reviews'),
    path('<int:course_id>/reviews/', views.create_review, name='create_review'),
    path('reviews/<int:review_id>/', views.edit_review, name='edit_review'),
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),

    # Notes
    path('<int:course_id>/notes/list/', views.get_course_notes, name='get_course_notes'),
    path('<int:course_id>/notes/', views.create_note, name='create_note'),
    path('notes/<int:note_id>/', views.edit_note, name='edit_note'),
    path('notes/<int:note_id>/delete/', views.delete_note, name='delete_note'),
]
