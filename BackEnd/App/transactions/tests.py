from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Transaction
from courses.models import Course

User = get_user_model()


class TransactionModelTest(TestCase):
    def setUp(self):
        # Create test users
        self.student = User.objects.create_user(
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student'
        )
        
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Instructor',
            role='instructor'
        )
        
        # Create test course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=99.99,
            instructor=self.instructor
        )
    
    def test_transaction_creation(self):
        """Test creating a transaction"""
        transaction = Transaction.objects.create(
            student=self.student,
            course=self.course,
            amount=99.99,
            payment_status='completed',
            stripe_payment_intent_id='pi_test123'
        )
        
        self.assertEqual(transaction.student, self.student)
        self.assertEqual(transaction.course, self.course)
        self.assertEqual(transaction.amount, 99.99)
        self.assertEqual(transaction.payment_status, 'completed')
        self.assertTrue(transaction.is_successful)
    
    def test_transaction_id_generation(self):
        """Test that transaction ID is generated automatically"""
        transaction = Transaction.objects.create(
            student=self.student,
            course=self.course,
            amount=99.99
        )
        
        self.assertTrue(transaction.transaction_id.startswith('TXN_'))
    
    def test_student_name_property(self):
        """Test student_name property"""
        transaction = Transaction.objects.create(
            student=self.student,
            course=self.course,
            amount=99.99
        )
        
        self.assertEqual(transaction.student_name, 'Test Student')
    
    def test_course_title_property(self):
        """Test course_title property"""
        transaction = Transaction.objects.create(
            student=self.student,
            course=self.course,
            amount=99.99
        )
        
        self.assertEqual(transaction.course_title, 'Test Course')
    
    def test_instructor_name_property(self):
        """Test instructor_name property"""
        transaction = Transaction.objects.create(
            student=self.student,
            course=self.course,
            amount=99.99
        )
        
        self.assertEqual(transaction.instructor_name, 'Test Instructor')
