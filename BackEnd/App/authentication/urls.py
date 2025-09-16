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
    path('instructor/request/me/', views.get_my_instructor_request,
         name='get_my_instructor_request'),
    path('instructor/upload_photo/', views.upload_instructor_photo,
         name='upload_instructor_photo'),
    path('instructor/requests/', views.list_instructor_requests,
         name='list_instructor_requests'),
    path('instructor/requests/<int:request_id>/approve/',
         views.approve_instructor, name='approve_instructor'),
    path('instructor/requests/<int:request_id>/reject/',
         views.reject_instructor, name='reject_instructor'),
    # Identity verification
    path('verification/request/', views.request_identity_verification,
         name='request_identity_verification'),
    path('verification/request/me/', views.get_my_verification_request,
         name='get_my_verification_request'),
    path('verification/requests/', views.list_identity_verification_requests,
         name='list_identity_verification_requests'),
    path('verification/requests/<int:request_id>/approve/',
         views.approve_identity_verification, name='approve_identity_verification'),
    path('verification/requests/<int:request_id>/reject/',
         views.reject_identity_verification, name='reject_identity_verification'),
    path('users/', views.list_users, name='list_users'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    # Admin management
    path('admin/create/', views.create_admin, name='create_admin'),
]
