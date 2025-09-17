"""
URL configuration for App project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count
from django.http import JsonResponse
from authentication.models import User, InstructorRequest
from courses.models import Course, Enrollment


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint for deployment monitoring"""
    try:
        return JsonResponse({
            'status': 'ok',
            'message': 'Educational Platform API is running'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


urlpatterns = [
    path('', health_check, name='health_check'),  # Root health check
    path('api/health/', health_check, name='api_health_check'),  # API health check
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/oauth2/', include('oauth2.urls')),
    path('api/exams/', include('exams.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/live/', include('liveSessions.urls')),
    path('api/', include('notifications.urls')),
    path('api/admin/analytics/', include('App.analytics_urls')),
    path('api/admin/sales/', include('App.sales_urls')),
    path('api/admin/categories/', include('App.admin_categories_urls')),
    path('api/chatbot/', include('chatBot.urls')),
    path('api/chat/', include('chat.urls')),  # Chat system endpoints
    # Payment transactions
    path('api/transactions/', include('transactions.urls')),
    path('api/instructor/', include('App.instructor_urls')),
]
