from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient
import json

from .models import Session, Participant
from .serializers import SessionSerializer, SessionCreateSerializer, SessionUpdateSerializer

User = get_user_model()


class SessionDateTestCase(TestCase):
    """Test cases specifically for date handling in tutoring sessions"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        # Create test dates
        self.future_date = timezone.now() + timedelta(days=1)
        self.past_date = timezone.now() - timedelta(days=1)
        self.current_date = timezone.now()

    def test_date_field_type(self):
        """Test that date field is properly defined as DateTimeField"""
        session = Session.objects.create(
            title="Test Session",
            description="Test Description",
            date=self.future_date,
            max_participants=5,
            creator=self.user
        )

        # Check that date is a datetime object
        self.assertIsInstance(session.date, datetime)
        self.assertEqual(session.date, self.future_date)

    def test_date_serialization(self):
        """Test that date is properly serialized"""
        session = Session.objects.create(
            title="Test Session",
            description="Test Description",
            date=self.future_date,
            max_participants=5,
            creator=self.user
        )

        serializer = SessionSerializer(session)
        data = serializer.data

        # Check that date is included in serialized data
        self.assertIn('date', data)

        # Check that date is a string (ISO format)
        self.assertIsInstance(data['date'], str)

        # Verify the date value is correct
        expected_date_str = self.future_date.isoformat().replace('+00:00', 'Z')
        self.assertEqual(data['date'], expected_date_str)

    def test_date_deserialization(self):
        """Test that date is properly deserialized from string"""
        # Test data with ISO format date string
        test_data = {
            'title': 'Test Session',
            'description': 'Test Description',
            'date': self.future_date.isoformat(),
            'max_participants': 5
        }

        serializer = SessionCreateSerializer(data=test_data, context={
                                             'request': type('MockRequest', (), {'user': self.user})()})

        self.assertTrue(serializer.is_valid())
        session = serializer.save()

        # Check that date was properly parsed
        self.assertEqual(session.date, self.future_date)

    def test_future_date_validation(self):
        """Test that only future dates are accepted"""
        # Test with past date
        past_data = {
            'title': 'Past Session',
            'description': 'Test Description',
            'date': self.past_date.isoformat(),
            'max_participants': 5
        }

        serializer = SessionCreateSerializer(data=past_data, context={
                                             'request': type('MockRequest', (), {'user': self.user})()})

        self.assertFalse(serializer.is_valid())
        self.assertIn('date', serializer.errors)
        self.assertIn('Session date must be in the future',
                      str(serializer.errors['date']))

        # Test with current date (should also fail)
        current_data = {
            'title': 'Current Session',
            'description': 'Test Description',
            'date': self.current_date.isoformat(),
            'max_participants': 5
        }

        serializer = SessionCreateSerializer(data=current_data, context={
                                             'request': type('MockRequest', (), {'user': self.user})()})

        self.assertFalse(serializer.is_valid())
        self.assertIn('date', serializer.errors)

        # Test with future date (should pass)
        future_data = {
            'title': 'Future Session',
            'description': 'Test Description',
            'date': self.future_date.isoformat(),
            'max_participants': 5
        }

        serializer = SessionCreateSerializer(data=future_data, context={
                                             'request': type('MockRequest', (), {'user': self.user})()})

        self.assertTrue(serializer.is_valid())

    def test_date_format_handling(self):
        """Test different date formats are handled properly"""
        # Test with different date formats
        future_date_str = self.future_date.strftime('%Y-%m-%d %H:%M:%S')

        test_data = {
            'title': 'Format Test Session',
            'description': 'Test Description',
            'date': future_date_str,
            'max_participants': 5
        }

        serializer = SessionCreateSerializer(data=test_data, context={
                                             'request': type('MockRequest', (), {'user': self.user})()})

        # This should work as Django handles various date formats
        self.assertTrue(serializer.is_valid())

    def test_date_update_validation(self):
        """Test date validation when updating sessions"""
        # Create a session with future date
        session = Session.objects.create(
            title="Test Session",
            description="Test Description",
            date=self.future_date,
            max_participants=5,
            creator=self.user
        )

        # Try to update with past date
        update_data = {
            'title': 'Updated Session',
            'description': 'Updated Description',
            'date': self.past_date.isoformat(),
            'max_participants': 5
        }

        serializer = SessionUpdateSerializer(session, data=update_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('date', serializer.errors)

        # Update with valid future date
        new_future_date = timezone.now() + timedelta(days=2)
        valid_update_data = {
            'title': 'Updated Session',
            'description': 'Updated Description',
            'date': new_future_date.isoformat(),
            'max_participants': 5
        }

        serializer = SessionUpdateSerializer(session, data=valid_update_data)

        self.assertTrue(serializer.is_valid())
        updated_session = serializer.save()
        self.assertEqual(updated_session.date, new_future_date)

    def test_date_edge_cases(self):
        """Test edge cases with dates"""
        # Test with date very close to current time
        almost_now = timezone.now() + timedelta(seconds=1)

        test_data = {
            'title': 'Edge Case Session',
            'description': 'Test Description',
            'date': almost_now.isoformat(),
            'max_participants': 5
        }

        serializer = SessionCreateSerializer(data=test_data, context={
                                             'request': type('MockRequest', (), {'user': self.user})()})

        # This should be valid as it's still in the future
        self.assertTrue(serializer.is_valid())

        # Test with date far in the future
        far_future = timezone.now() + timedelta(days=365)

        test_data_far = {
            'title': 'Far Future Session',
            'description': 'Test Description',
            'date': far_future.isoformat(),
            'max_participants': 5
        }

        serializer = SessionCreateSerializer(data=test_data_far, context={
                                             'request': type('MockRequest', (), {'user': self.user})()})

        self.assertTrue(serializer.is_valid())


class SessionDateAPITestCase(APITestCase):
    """API test cases for date handling"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)

        self.future_date = timezone.now() + timedelta(days=1)
        self.past_date = timezone.now() - timedelta(days=1)

    def test_create_session_with_valid_date(self):
        """Test creating a session with valid future date via API"""
        data = {
            'title': 'API Test Session',
            'description': 'Test Description',
            'date': self.future_date.isoformat(),
            'max_participants': 5
        }

        response = self.client.post('/api/sessions/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that date is properly saved and returned
        session_data = response.data
        self.assertIn('date', session_data)
        self.assertEqual(session_data['title'], 'API Test Session')

    def test_create_session_with_invalid_date(self):
        """Test creating a session with past date via API"""
        data = {
            'title': 'Invalid Date Session',
            'description': 'Test Description',
            'date': self.past_date.isoformat(),
            'max_participants': 5
        }

        response = self.client.post('/api/sessions/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date', response.data)

    def test_get_session_date_format(self):
        """Test that session date is returned in proper format via API"""
        # Create a session
        session = Session.objects.create(
            title="Test Session",
            description="Test Description",
            date=self.future_date,
            max_participants=5,
            creator=self.user
        )

        # Get the session via API
        response = self.client.get(f'/api/sessions/{session.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check date format
        session_data = response.data
        self.assertIn('date', session_data)
        self.assertIsInstance(session_data['date'], str)

        # Verify it's in ISO format
        expected_date_str = self.future_date.isoformat().replace('+00:00', 'Z')
        self.assertEqual(session_data['date'], expected_date_str)

    def test_update_session_date(self):
        """Test updating session date via API"""
        # Create a session
        session = Session.objects.create(
            title="Test Session",
            description="Test Description",
            date=self.future_date,
            max_participants=5,
            creator=self.user
        )

        # Update with new future date
        new_future_date = timezone.now() + timedelta(days=2)
        update_data = {
            'title': 'Updated Session',
            'description': 'Updated Description',
            'date': new_future_date.isoformat(),
            'max_participants': 5
        }

        response = self.client.put(
            f'/api/sessions/{session.id}/', update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that date was updated
        session_data = response.data
        expected_date_str = new_future_date.isoformat().replace('+00:00', 'Z')
        self.assertEqual(session_data['date'], expected_date_str)

    def test_update_session_with_invalid_date(self):
        """Test updating session with past date via API"""
        # Create a session
        session = Session.objects.create(
            title="Test Session",
            description="Test Description",
            date=self.future_date,
            max_participants=5,
            creator=self.user
        )

        # Try to update with past date
        update_data = {
            'title': 'Updated Session',
            'description': 'Updated Description',
            'date': self.past_date.isoformat(),
            'max_participants': 5
        }

        response = self.client.put(
            f'/api/sessions/{session.id}/', update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date', response.data)


if __name__ == '__main__':
    # Run the tests
    import django
    django.setup()

    # Create a test runner
    from django.test.utils import get_runner
    from django.conf import settings

    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    # Run the tests
    failures = test_runner.run_tests(['tutoring_sessions.tests'])

    if failures:
        print(f"Tests failed: {failures}")
    else:
        print("All date tests passed!")
