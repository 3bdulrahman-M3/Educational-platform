from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/request/', views.password_reset_request,
         name='password_reset_request'),
    path('password-reset/confirm/', views.password_reset_confirm,
         name='password_reset_confirm'),
    path('instructor/request/', views.request_instructor,
         name='request_instructor'),
    path('instructor/requests/', views.list_instructor_requests,
         name='list_instructor_requests'),
    path('instructor/requests/<int:request_id>/approve/',
         views.approve_instructor, name='approve_instructor'),
    path('instructor/requests/<int:request_id>/reject/',
         views.reject_instructor, name='reject_instructor'),
    path('users/', views.list_users, name='list_users'),
]
