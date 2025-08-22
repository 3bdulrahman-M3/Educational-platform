from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    PRICING_CHOICES = [
        ('free', 'Free'),
        ('paid', 'Paid'),
        ('subscription', 'Subscription Required'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, db_column='Price')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Original price before discount")
    discount_percentage = models.PositiveIntegerField(default=0, help_text="Discount percentage (0-100)")
    pricing_type = models.CharField(max_length=20, choices=PRICING_CHOICES, default='free')
    duration = models.PositiveIntegerField(default=0, help_text="Duration in minutes")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_courses',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_free(self):
        return self.price == 0 or self.pricing_type == 'free'
    
    @property
    def has_discount(self):
        return self.original_price and self.original_price > self.price
    
    @property
    def discount_amount(self):
        if self.has_discount:
            return self.original_price - self.price
        return 0
    
    @property
    def display_price(self):
        if self.is_free:
            return "Free"
        return f"${self.price}"
    
    @property
    def display_original_price(self):
        if self.has_discount:
            return f"${self.original_price}"
        return None

class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.email} enrolled in {self.course.title}"


class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    # Optional direct URL if instructor wants to link from YouTube/Vimeo/etc.
    url = models.URLField(max_length=1000, blank=True, null=True)
    # Optional uploaded video file via Cloudinary
    file = CloudinaryField('video', resource_type='video', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Purchase(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('fake', 'Fake Payment'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='purchases')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='stripe')
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    purchased_at = models.DateTimeField(auto_now_add=True)
    payment_completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student.email} purchased {self.course.title} for ${self.amount_paid}"
    
    @property
    def is_paid(self):
        return self.payment_status == 'completed'
    
    def mark_as_paid(self, transaction_id=None):
        from django.utils import timezone
        self.payment_status = 'completed'
        self.payment_completed_at = timezone.now()
        if transaction_id:
            self.transaction_id = transaction_id
        self.save()
        
        # Auto-enroll student after successful payment
        Enrollment.objects.get_or_create(
            student=self.student,
            course=self.course
        )


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Order {self.id} by {self.student.email} - ${self.total_amount}"
    
    @property
    def items_count(self):
        return self.order_items.count()
    
    def add_course(self, course, price):
        OrderItem.objects.create(
            order=self,
            course=course,
            price=price
        )
    
    def complete_order(self):
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        
        # Create purchases for all items
        for item in self.order_items.all():
            Purchase.objects.create(
                student=self.student,
                course=item.course,
                amount_paid=item.price,
                payment_status='completed',
                payment_method='stripe'  # Default, can be updated
            )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.course.title} - ${self.price}"