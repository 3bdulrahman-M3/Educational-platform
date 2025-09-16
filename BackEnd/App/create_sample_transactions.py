#!/usr/bin/env python
"""
Script to create sample transaction data for testing
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()

from transactions.models import Transaction
from authentication.models import User
from courses.models import Course

def create_sample_transactions():
    """Create sample transaction data"""
    
    # Get or create a sample user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'first_name': 'أحمد',
            'last_name': 'محمد',
            'role': 'student',
            'is_active': True
        }
    )
    
    # Get or create a sample course
    course, created = Course.objects.get_or_create(
        title='تعلم React',
        defaults={
            'description': 'دورة تعلم React للمبتدئين',
            'price': 99.99,
            'instructor': User.objects.filter(role='instructor').first() or user,
            'status': 'approved'
        }
    )
    
    # Create sample transactions
    sample_transactions = [
        {
            'student': user,
            'course': course,
            'amount': 99.99,
            'currency': 'USD',
            'payment_status': 'completed',
            'payment_method': 'stripe',
            'stripe_payment_intent_id': f'pi_test_{random.randint(100000, 999999)}',
            'notes': f'Enrollment in {course.title}',
            'metadata': {
                'course_id': course.id,
                'student_id': user.id,
                'enrollment_date': datetime.now().isoformat()
            }
        },
        {
            'student': user,
            'course': course,
            'amount': 149.99,
            'currency': 'USD',
            'payment_status': 'pending',
            'payment_method': 'stripe',
            'stripe_payment_intent_id': f'pi_test_{random.randint(100000, 999999)}',
            'notes': f'Enrollment in {course.title} - Pending',
            'metadata': {
                'course_id': course.id,
                'student_id': user.id,
                'enrollment_date': datetime.now().isoformat()
            }
        },
        {
            'student': user,
            'course': course,
            'amount': 199.99,
            'currency': 'USD',
            'payment_status': 'failed',
            'payment_method': 'stripe',
            'stripe_payment_intent_id': f'pi_test_{random.randint(100000, 999999)}',
            'notes': f'Enrollment in {course.title} - Failed',
            'metadata': {
                'course_id': course.id,
                'student_id': user.id,
                'enrollment_date': datetime.now().isoformat()
            }
        }
    ]
    
    created_count = 0
    for i, transaction_data in enumerate(sample_transactions):
        # Make stripe_payment_intent_id unique
        transaction_data['stripe_payment_intent_id'] = f'pi_test_{random.randint(100000, 999999)}_{i}'
        
        try:
            transaction, created = Transaction.objects.get_or_create(
                stripe_payment_intent_id=transaction_data['stripe_payment_intent_id'],
                defaults=transaction_data
            )
            if created:
                created_count += 1
                print(f"Created transaction: {transaction.transaction_id}")
        except Exception as e:
            print(f"Error creating transaction {i}: {e}")
            continue
    
    print(f"\nCreated {created_count} sample transactions")
    print(f"Total transactions in database: {Transaction.objects.count()}")

if __name__ == '__main__':
    create_sample_transactions()
