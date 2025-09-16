from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .models import Transaction
from .serializers import (
    TransactionSerializer,
    TransactionCreateSerializer,
    TransactionUpdateSerializer,
    TransactionListSerializer
)
from courses.models import Course
from authentication.models import User


class TransactionPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TransactionListCreateView(generics.ListCreateAPIView):
    """
    List all transactions or create a new transaction
    """
    queryset = Transaction.objects.all()
    pagination_class = TransactionPagination
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TransactionCreateSerializer
        return TransactionListSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            # Only admins can view all transactions
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        else:
            # Students can create transactions
            return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Add search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__email__icontains=search) |
                Q(course__title__icontains=search) |
                Q(transaction_id__icontains=search)
            )
        
        # Filter by payment status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(payment_status=status)
        
        # Filter by payment method
        payment_method = self.request.query_params.get('payment_method', None)
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        # Filter by student
        student = self.request.query_params.get('student', None)
        if student:
            queryset = queryset.filter(student_id=student)
        
        # Filter by course
        course = self.request.query_params.get('course', None)
        if course:
            queryset = queryset.filter(course_id=course)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset.select_related('student', 'course', 'course__instructor')


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a transaction
    """
    queryset = Transaction.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TransactionUpdateSerializer
        return TransactionSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            # Admins can view any transaction, users can view their own
            return [permissions.IsAuthenticated()]
        else:
            # Only admins can update/delete transactions
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def transaction_stats(request):
    """
    Get transaction statistics for admin dashboard
    """
    # Total revenue
    total_revenue = Transaction.objects.filter(
        payment_status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Transaction counts by status
    status_counts = Transaction.objects.values('payment_status').annotate(
        count=Count('id')
    ).order_by('payment_status')
    
    # Recent transactions (last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    recent_transactions = Transaction.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    
    # Monthly revenue (current month)
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = Transaction.objects.filter(
        payment_status='completed',
        created_at__gte=current_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    return Response({
        'total_revenue': float(total_revenue),
        'monthly_revenue': float(monthly_revenue),
        'recent_transactions': recent_transactions,
        'status_counts': list(status_counts),
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_transaction_from_enrollment(request):
    """
    Create a transaction when a student enrolls in a course
    This should be called after successful payment
    """
    try:
        course_id = request.data.get('course_id')
        stripe_payment_intent_id = request.data.get('stripe_payment_intent_id')
        
        if not course_id or not stripe_payment_intent_id:
            return Response({
                'error': 'course_id and stripe_payment_intent_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get course
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({
                'error': 'Course not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if transaction already exists
        if Transaction.objects.filter(
            stripe_payment_intent_id=stripe_payment_intent_id
        ).exists():
            return Response({
                'error': 'Transaction already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create transaction
        transaction = Transaction.objects.create(
            student=request.user,
            course=course,
            amount=course.price,
            currency='USD',
            payment_status='completed',
            payment_method='stripe',
            stripe_payment_intent_id=stripe_payment_intent_id,
            notes=f'Enrollment in {course.title}',
            metadata={
                'enrollment_date': timezone.now().isoformat(),
                'course_id': course.id,
                'student_id': request.user.id,
            }
        )
        
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_transactions(request):
    """
    Get transactions for the current user
    """
    transactions = Transaction.objects.filter(
        student=request.user
    ).select_related('course', 'course__instructor').order_by('-created_at')
    
    # Add search functionality
    search = request.query_params.get('search', None)
    if search:
        transactions = transactions.filter(
            Q(course__title__icontains=search) |
            Q(transaction_id__icontains=search)
        )
    
    # Pagination
    paginator = TransactionPagination()
    page = paginator.paginate_queryset(transactions, request)
    
    if page is not None:
        serializer = TransactionListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = TransactionListSerializer(transactions, many=True)
    return Response(serializer.data)
