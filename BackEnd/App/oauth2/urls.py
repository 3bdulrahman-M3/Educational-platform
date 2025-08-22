from django.urls import path
from . import views

urlpatterns = [
    path('google/auth-url/', views.google_auth_url, name='google_auth_url'),
    path('google/callback/', views.google_auth_callback, name='google_auth_callback'),
]
