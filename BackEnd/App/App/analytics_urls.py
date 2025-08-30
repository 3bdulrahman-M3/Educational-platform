from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from authentication.models import User, InstructorRequest
from courses.models import Course, Enrollment


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def summary(request):
    if request.user.role != 'admin':
        return Response({'error': 'Forbidden'}, status=403)

    total_users = User.objects.count()
    total_instructors = User.objects.filter(role='instructor').count()
    total_courses = Course.objects.count()
    pending_instructor_requests = InstructorRequest.objects.filter(
        status='pending').count()
    pending_courses = Course.objects.filter(status='pending').count()

    # Completions per course: approximate by enrollments for now (placeholder)
    completions = (
        Enrollment.objects
        .values('course_id')
        .annotate(count=Count('id'))
        .order_by('-count')[:20]
    )
    completions_by_course = {
        str(item['course_id']): item['count'] for item in completions}

    return Response({
        'totals': {
            'users': total_users,
            'instructors': total_instructors,
            'courses': total_courses,
        },
        'pending': {
            'instructor_requests': pending_instructor_requests,
            'courses': pending_courses,
        },
        'completions_by_course': completions_by_course,
    })


urlpatterns = [
    path('summary/', summary, name='admin_analytics_summary'),
]
