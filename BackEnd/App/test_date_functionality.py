#!/usr/bin/env python
"""
Standalone test script to test date functionality in tutoring sessions
"""

from tutoring_sessions.serializers import SessionSerializer, SessionCreateSerializer, SessionUpdateSerializer
from tutoring_sessions.models import Session
from django.utils import timezone
from django.contrib.auth import get_user_model
import os
import sys
import django
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()


User = get_user_model()


def test_date_functionality():
    """Test date functionality in tutoring sessions"""
    print("🧪 Testing Date Functionality in Tutoring Sessions")
    print("=" * 60)

    # Create test user
    try:
        user = User.objects.create_user(
            username='testuser_date',
            email='test_date@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print("✅ Test user created successfully")
    except Exception as e:
        print(f"❌ Failed to create test user: {e}")
        return

    # Test dates
    future_date = timezone.now() + timedelta(days=1)
    past_date = timezone.now() - timedelta(days=1)
    current_date = timezone.now()

    print(f"\n📅 Test Dates:")
    print(f"   Future date: {future_date}")
    print(f"   Past date: {past_date}")
    print(f"   Current date: {current_date}")

    # Test 1: Create session with future date
    print(f"\n🔍 Test 1: Creating session with future date")
    try:
        session = Session.objects.create(
            title="Future Session Test",
            description="Test session with future date",
            date=future_date,
            max_participants=5,
            creator=user
        )
        print(f"   ✅ Session created: {session.title}")
        print(f"   📅 Session date: {session.date}")
        print(f"   🔍 Date type: {type(session.date)}")
        print(f"   🔍 Is datetime: {isinstance(session.date, datetime)}")
    except Exception as e:
        print(f"   ❌ Failed to create session: {e}")
        return

    # Test 2: Serialize session and check date format
    print(f"\n🔍 Test 2: Serializing session date")
    try:
        serializer = SessionSerializer(session)
        data = serializer.data

        print(f"   ✅ Serialization successful")
        print(f"   📅 Serialized date: {data.get('date')}")
        print(f"   🔍 Date type in serialized data: {type(data.get('date'))}")
        print(f"   🔍 Is string: {isinstance(data.get('date'), str)}")

        # Check if date is in ISO format
        if data.get('date'):
            expected_date_str = future_date.isoformat().replace('+00:00', 'Z')
            print(f"   🔍 Expected ISO format: {expected_date_str}")
            print(
                f"   🔍 Matches expected: {data.get('date') == expected_date_str}")
    except Exception as e:
        print(f"   ❌ Serialization failed: {e}")

    # Test 3: Deserialize date from string
    print(f"\n🔍 Test 3: Deserializing date from string")
    try:
        test_data = {
            'title': 'Deserialize Test Session',
            'description': 'Test deserialization',
            'date': future_date.isoformat(),
            'max_participants': 5
        }

        # Create mock request context
        mock_request = type('MockRequest', (), {'user': user})()
        serializer = SessionCreateSerializer(
            data=test_data, context={'request': mock_request})

        if serializer.is_valid():
            new_session = serializer.save()
            print(f"   ✅ Deserialization successful")
            print(f"   📅 Parsed date: {new_session.date}")
            print(
                f"   🔍 Date matches original: {new_session.date == future_date}")
        else:
            print(
                f"   ❌ Deserialization validation failed: {serializer.errors}")
    except Exception as e:
        print(f"   ❌ Deserialization failed: {e}")

    # Test 4: Validate future date requirement
    print(f"\n🔍 Test 4: Validating future date requirement")
    try:
        # Test with past date (should fail)
        past_data = {
            'title': 'Past Session',
            'description': 'Should fail validation',
            'date': past_date.isoformat(),
            'max_participants': 5
        }

        mock_request = type('MockRequest', (), {'user': user})()
        serializer = SessionCreateSerializer(
            data=past_data, context={'request': mock_request})

        if not serializer.is_valid():
            print(f"   ✅ Past date correctly rejected")
            print(f"   📝 Error message: {serializer.errors.get('date')}")
        else:
            print(f"   ❌ Past date should have been rejected")

        # Test with current date (should also fail)
        current_data = {
            'title': 'Current Session',
            'description': 'Should also fail validation',
            'date': current_date.isoformat(),
            'max_participants': 5
        }

        serializer = SessionCreateSerializer(
            data=current_data, context={'request': mock_request})

        if not serializer.is_valid():
            print(f"   ✅ Current date correctly rejected")
            print(f"   📝 Error message: {serializer.errors.get('date')}")
        else:
            print(f"   ❌ Current date should have been rejected")

    except Exception as e:
        print(f"   ❌ Date validation test failed: {e}")

    # Test 5: Test date format handling
    print(f"\n🔍 Test 5: Testing different date formats")
    try:
        # Test with different date format
        future_date_str = future_date.strftime('%Y-%m-%d %H:%M:%S')

        format_data = {
            'title': 'Format Test Session',
            'description': 'Testing date format handling',
            'date': future_date_str,
            'max_participants': 5
        }

        mock_request = type('MockRequest', (), {'user': user})()
        serializer = SessionCreateSerializer(
            data=format_data, context={'request': mock_request})

        if serializer.is_valid():
            format_session = serializer.save()
            print(f"   ✅ Date format handling successful")
            print(f"   📅 Input format: {future_date_str}")
            print(f"   📅 Parsed date: {format_session.date}")
        else:
            print(f"   ❌ Date format handling failed: {serializer.errors}")
    except Exception as e:
        print(f"   ❌ Date format test failed: {e}")

    # Test 6: Test edge cases
    print(f"\n🔍 Test 6: Testing edge cases")
    try:
        # Test with date very close to current time
        almost_now = timezone.now() + timedelta(seconds=1)

        edge_data = {
            'title': 'Edge Case Session',
            'description': 'Testing edge case with date very close to now',
            'date': almost_now.isoformat(),
            'max_participants': 5
        }

        mock_request = type('MockRequest', (), {'user': user})()
        serializer = SessionCreateSerializer(
            data=edge_data, context={'request': mock_request})

        if serializer.is_valid():
            print(f"   ✅ Edge case (1 second in future) accepted")
        else:
            print(f"   ❌ Edge case rejected: {serializer.errors}")

        # Test with date far in the future
        far_future = timezone.now() + timedelta(days=365)

        far_future_data = {
            'title': 'Far Future Session',
            'description': 'Testing date far in the future',
            'date': far_future.isoformat(),
            'max_participants': 5
        }

        serializer = SessionCreateSerializer(
            data=far_future_data, context={'request': mock_request})

        if serializer.is_valid():
            print(f"   ✅ Far future date (1 year) accepted")
        else:
            print(f"   ❌ Far future date rejected: {serializer.errors}")

    except Exception as e:
        print(f"   ❌ Edge case test failed: {e}")

    # Clean up
    print(f"\n🧹 Cleaning up test data...")
    try:
        Session.objects.filter(creator=user).delete()
        user.delete()
        print(f"   ✅ Test data cleaned up")
    except Exception as e:
        print(f"   ❌ Cleanup failed: {e}")

    print(f"\n🎉 Date functionality testing completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_date_functionality()
