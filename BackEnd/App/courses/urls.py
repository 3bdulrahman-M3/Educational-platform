from django.urls import path
from . import views

urlpatterns = [
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
    path('student/courses/', views.get_current_user_enrollments, name='get_current_user_enrollments'),
    path('student/<int:student_id>/enrollments/',
         views.get_student_enrollments, name='get_student_enrollments'),
    path('instructor/<int:instructor_id>/courses/',
         views.get_instructor_with_courses, name='get_instructor_with_courses'),
    path('<int:pk>/notify-students/',
         views.notify_students, name='notify_students'),
    
    # Purchase endpoints
    path('<int:course_id>/purchase/', views.purchase_course, name='purchase_course'),
    path('purchases/<int:purchase_id>/confirm/', views.confirm_purchase, name='confirm_purchase'),
    path('purchases/my/', views.get_my_purchases, name='get_my_purchases'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/<int:order_id>/complete/', views.complete_order, name='complete_order'),
    path('orders/my/', views.get_my_orders, name='get_my_orders'),
    path('<int:course_id>/access/', views.check_course_access, name='check_course_access'),
]
