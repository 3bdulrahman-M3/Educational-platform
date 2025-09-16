from rest_framework import serializers
from .models import Transaction
from authentication.serializers import UserProfileSerializer
from courses.serializers import CourseSerializer


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model with basic information
    """
    student = UserProfileSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    student_name = serializers.ReadOnlyField()
    student_email = serializers.ReadOnlyField()
    course_title = serializers.ReadOnlyField()
    instructor_name = serializers.ReadOnlyField()
    is_successful = serializers.ReadOnlyField()
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'transaction_id',
            'student',
            'course',
            'amount',
            'currency',
            'payment_status',
            'payment_method',
            'stripe_payment_intent_id',
            'stripe_charge_id',
            'created_at',
            'updated_at',
            'completed_at',
            'notes',
            'metadata',
            'student_name',
            'student_email',
            'course_title',
            'instructor_name',
            'is_successful',
        ]
        read_only_fields = [
            'id',
            'transaction_id',
            'created_at',
            'updated_at',
            'completed_at',
        ]


class TransactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new transactions
    """
    class Meta:
        model = Transaction
        fields = [
            'student',
            'course',
            'amount',
            'currency',
            'payment_method',
            'stripe_payment_intent_id',
            'notes',
            'metadata',
        ]
    
    def create(self, validated_data):
        # Set payment status to pending by default
        validated_data['payment_status'] = 'pending'
        return super().create(validated_data)


class TransactionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating transaction status
    """
    class Meta:
        model = Transaction
        fields = [
            'payment_status',
            'stripe_charge_id',
            'notes',
            'metadata',
        ]
    
    def update(self, instance, validated_data):
        # Set completed_at when status changes to completed
        if validated_data.get('payment_status') == 'completed' and not instance.completed_at:
            from django.utils import timezone
            instance.completed_at = timezone.now()
        
        return super().update(instance, validated_data)


class TransactionListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for transaction lists (admin view)
    """
    student_name = serializers.ReadOnlyField()
    student_email = serializers.ReadOnlyField()
    course_title = serializers.ReadOnlyField()
    instructor_name = serializers.ReadOnlyField()
    is_successful = serializers.ReadOnlyField()
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'transaction_id',
            'student_name',
            'student_email',
            'course_title',
            'instructor_name',
            'amount',
            'currency',
            'payment_status',
            'payment_method',
            'created_at',
            'completed_at',
            'is_successful',
        ]
