from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id',
        'student_name',
        'course_title',
        'amount',
        'currency',
        'payment_status',
        'payment_method',
        'created_at',
        'completed_at',
    ]
    
    list_filter = [
        'payment_status',
        'payment_method',
        'currency',
        'created_at',
        'completed_at',
    ]
    
    search_fields = [
        'transaction_id',
        'student__first_name',
        'student__last_name',
        'student__email',
        'course__title',
        'stripe_payment_intent_id',
        'stripe_charge_id',
    ]
    
    readonly_fields = [
        'transaction_id',
        'created_at',
        'updated_at',
        'completed_at',
        'student_name',
        'course_title',
        'instructor_name',
        'is_successful',
    ]
    
    fieldsets = (
        ('Transaction Info', {
            'fields': (
                'transaction_id',
                'student',
                'course',
                'amount',
                'currency',
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_status',
                'payment_method',
                'stripe_payment_intent_id',
                'stripe_charge_id',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at',
            )
        }),
        ('Additional Info', {
            'fields': (
                'notes',
                'metadata',
            )
        }),
        ('Computed Fields', {
            'fields': (
                'student_name',
                'course_title',
                'instructor_name',
                'is_successful',
            ),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'course', 'course__instructor'
        )
