from django.urls import path
from . import views

urlpatterns = [
    path('sessions/create/', views.create_session, name='create_session'),
    path('sessions/', views.list_sessions, name='list_sessions'),
    path('sessions/<int:pk>/', views.session_detail, name='session_detail'),
    path("jaas-token/", views.generate_jaas_token, name="generate_jaas_token"),
    path('sessions/<int:pk>/edit/', views.edit_session, name='edit_session'),
    path('sessions/<int:pk>/delete/', views.delete_session, name='delete_session'),
]