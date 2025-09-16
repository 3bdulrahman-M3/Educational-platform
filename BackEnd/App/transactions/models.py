from django.db import models
from django.conf import settings
from django.utils import timezone


class Transaction(models.Model):
    """
    Represents a payment transaction for course enrollment.
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]
    
    # Basic transaction info
    id = models.AutoField(primary_key=True)
    transaction_id = models.CharField(max_length=100, unique=True, help_text="Unique transaction identifier")
    
    # User and course info
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text="Student who made the payment"
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text="Course being purchased"
    )
    
    # Payment details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Transaction amount in USD"
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text="Currency code"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        help_text="Current payment status"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='stripe',
        help_text="Payment method used"
    )
    
    # Stripe integration
    stripe_payment_intent_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Stripe PaymentIntent ID"
    )
    stripe_charge_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Stripe Charge ID"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When payment was completed"
    )
    
    # Additional info
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional transaction notes"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional transaction metadata"
    )
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'transactions'
        indexes = [
            models.Index(fields=['student', 'created_at']),
            models.Index(fields=['course', 'created_at']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.student.email} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        # Generate transaction ID if not provided
        if not self.transaction_id:
            self.transaction_id = f"TXN_{timezone.now().strftime('%Y%m%d%H%M%S')}_{self.id or 'NEW'}"
        
        # Set completed_at when status changes to completed
        if self.payment_status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_successful(self):
        """Check if transaction was successful"""
        return self.payment_status == 'completed'
    
    @property
    def student_name(self):
        """Get student's full name"""
        return f"{self.student.first_name} {self.student.last_name}".strip()
    
    @property
    def student_email(self):
        """Get student's email"""
        return self.student.email
    
    @property
    def course_title(self):
        """Get course title"""
        return self.course.title
    
    @property
    def instructor_name(self):
        """Get instructor's full name"""
        return f"{self.course.instructor.first_name} {self.course.instructor.last_name}".strip()
