from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('user/', views.user, name='user'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('role/update/', views.update_role, name='update_role'),
    path('google/', views.google_auth, name='google_auth'),
    path('google/complete/', views.google_complete, name='google_complete'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
