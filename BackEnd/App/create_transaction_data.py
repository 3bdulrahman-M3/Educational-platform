#!/usr/bin/env python
"""
Script to create sample transaction data for testing
"""
import os
import sys
import django
from django.utils import timezone
from datetime import timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()

from authentication.models import User
from courses.models import Course
from transactions.models import Transaction

def create_sample_transactions():
    """Create sample transaction data"""
    
    # Get or create test users
    student1, _ = User.objects.get_or_create(
        email='student1@test.com',
        defaults={
            'first_name': 'أحمد',
            'last_name': 'محمد',
            'role': 'student',
            'is_active': True
        }
    )
    
    student2, _ = User.objects.get_or_create(
        email='student2@test.com',
        defaults={
            'first_name': 'فاطمة',
            'last_name': 'علي',
            'role': 'student',
            'is_active': True
        }
    )
    
    student3, _ = User.objects.get_or_create(
        email='student3@test.com',
        defaults={
            'first_name': 'خالد',
            'last_name': 'سعد',
            'role': 'student',
            'is_active': True
        }
    )
    
    # Get or create instructor
    instructor, _ = User.objects.get_or_create(
        email='instructor@test.com',
        defaults={
            'first_name': 'سارة',
            'last_name': 'أحمد',
            'role': 'instructor',
            'is_active': True
        }
    )
    
    # Get or create courses
    course1, _ = Course.objects.get_or_create(
        title='تعلم React',
        defaults={
            'description': 'دورة شاملة لتعلم React',
            'price': 99.99,
            'instructor': instructor,
            'is_approved': True
        }
    )
    
    course2, _ = Course.objects.get_or_create(
        title='تعلم JavaScript',
        defaults={
            'description': 'دورة شاملة لتعلم JavaScript',
            'price': 149.99,
            'instructor': instructor,
            'is_approved': True
        }
    )
    
    course3, _ = Course.objects.get_or_create(
        title='تعلم Python',
        defaults={
            'description': 'دورة شاملة لتعلم Python',
            'price': 199.99,
            'instructor': instructor,
            'is_approved': True
        }
    )
    
    # Create sample transactions
    transactions_data = [
        {
            'student': student1,
            'course': course1,
            'amount': 99.99,
            'payment_status': 'completed',
            'payment_method': 'stripe',
            'stripe_payment_intent_id': 'pi_test_001',
            'notes': 'Enrollment in React course',
            'created_at': timezone.now() - timedelta(days=5)
        },
        {
            'student': student2,
            'course': course2,
            'amount': 149.99,
            'payment_status': 'pending',
            'payment_method': 'stripe',
            'stripe_payment_intent_id': 'pi_test_002',
            'notes': 'Enrollment in JavaScript course',
            'created_at': timezone.now() - timedelta(days=3)
        },
        {
            'student': student3,
            'course': course3,
            'amount': 199.99,
            'payment_status': 'completed',
            'payment_method': 'stripe',
            'stripe_payment_intent_id': 'pi_test_003',
            'notes': 'Enrollment in Python course',
            'created_at': timezone.now() - timedelta(days=1)
        },
        {
            'student': student1,
            'course': course2,
            'amount': 149.99,
            'payment_status': 'failed',
            'payment_method': 'stripe',
            'stripe_payment_intent_id': 'pi_test_004',
            'notes': 'Failed enrollment in JavaScript course',
            'created_at': timezone.now() - timedelta(hours=12)
        },
        {
            'student': student2,
            'course': course1,
            'amount': 99.99,
            'payment_status': 'completed',
            'payment_method': 'stripe',
            'stripe_payment_intent_id': 'pi_test_005',
            'notes': 'Enrollment in React course',
            'created_at': timezone.now() - timedelta(hours=6)
        }
    ]
    
    created_count = 0
    for data in transactions_data:
        transaction, created = Transaction.objects.get_or_create(
            stripe_payment_intent_id=data['stripe_payment_intent_id'],
            defaults=data
        )
        if created:
            created_count += 1
            print(f"Created transaction: {transaction.transaction_id}")
        else:
            print(f"Transaction already exists: {transaction.transaction_id}")
    
    print(f"\nCreated {created_count} new transactions")
    print(f"Total transactions: {Transaction.objects.count()}")
    
    # Print summary
    print("\nTransaction Summary:")
    for status, count in Transaction.objects.values('payment_status').annotate(
        count=django.db.models.Count('id')
    ).values_list('payment_status', 'count'):
        print(f"  {status}: {count}")

if __name__ == '__main__':
    create_sample_transactions()
