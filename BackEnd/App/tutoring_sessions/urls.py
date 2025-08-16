from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SessionViewSet,
    NotificationViewSet,
    SessionMaterialViewSet,
    start_session,
    end_session,
    join_live_session,
    leave_live_session
)

router = DefaultRouter()
router.register(r'sessions', SessionViewSet, basename='session')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/sessions/<int:session_pk>/materials/',
         SessionMaterialViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='session-materials'),
    path('api/sessions/<int:session_pk>/materials/<int:pk>/',
         SessionMaterialViewSet.as_view(
             {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='session-material-detail'),

    # Live Session Endpoints
    path('api/sessions/<int:session_id>/start/',
         start_session, name='start_session'),
    path('api/sessions/<int:session_id>/end/', end_session, name='end_session'),
    path('api/sessions/<int:session_id>/join_live/',
         join_live_session, name='join_live_session'),
    path('api/sessions/<int:session_id>/leave_live/',
         leave_live_session, name='leave_live_session'),
]
