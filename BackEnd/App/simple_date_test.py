#!/usr/bin/env python
"""
Simple test script to test date validation logic in tutoring sessions
"""

from datetime import datetime, timedelta
import pytz


def test_date_validation_logic():
    """Test the date validation logic that would be used in serializers"""
    print("🧪 Testing Date Validation Logic")
    print("=" * 50)

    # Create test dates
    now = datetime.now(pytz.UTC)
    future_date = now + timedelta(days=1)
    past_date = now - timedelta(days=1)
    current_date = now

    print(f"📅 Test Dates:")
    print(f"   Now: {now}")
    print(f"   Future date: {future_date}")
    print(f"   Past date: {past_date}")
    print(f"   Current date: {current_date}")

    # Test 1: Future date validation
    print(f"\n🔍 Test 1: Future date validation")
    if future_date > now:
        print(f"   ✅ Future date correctly identified as future")
    else:
        print(f"   ❌ Future date incorrectly identified")

    # Test 2: Past date validation
    print(f"\n🔍 Test 2: Past date validation")
    if past_date <= now:
        print(f"   ✅ Past date correctly identified as past/current")
    else:
        print(f"   ❌ Past date incorrectly identified")

    # Test 3: Current date validation
    print(f"\n🔍 Test 3: Current date validation")
    if current_date <= now:
        print(f"   ✅ Current date correctly identified as current/past")
    else:
        print(f"   ❌ Current date incorrectly identified")

    # Test 4: Date format handling
    print(f"\n🔍 Test 4: Date format handling")

    # Test ISO format
    future_iso = future_date.isoformat()
    print(f"   📅 ISO format: {future_iso}")
    print(f"   🔍 Type: {type(future_iso)}")

    # Test different formats
    future_str = future_date.strftime('%Y-%m-%d %H:%M:%S')
    print(f"   📅 String format: {future_str}")
    print(f"   🔍 Type: {type(future_str)}")

    # Test 5: Edge cases
    print(f"\n🔍 Test 5: Edge cases")

    # Very close to now
    almost_now = now + timedelta(seconds=1)
    if almost_now > now:
        print(f"   ✅ Date 1 second in future correctly identified as future")
    else:
        print(f"   ❌ Date 1 second in future incorrectly identified")

    # Far in the future
    far_future = now + timedelta(days=365)
    if far_future > now:
        print(f"   ✅ Date 1 year in future correctly identified as future")
    else:
        print(f"   ❌ Date 1 year in future incorrectly identified")

    # Test 6: Timezone handling
    print(f"\n🔍 Test 6: Timezone handling")

    # Test with different timezones
    utc_now = datetime.now(pytz.UTC)
    est_tz = pytz.timezone('US/Eastern')
    est_now = datetime.now(est_tz)

    print(f"   📅 UTC now: {utc_now}")
    print(f"   📅 EST now: {est_now}")
    print(
        f"   🔍 Both are datetime objects: {isinstance(utc_now, datetime) and isinstance(est_now, datetime)}")

    # Test 7: Date comparison logic
    print(f"\n🔍 Test 7: Date comparison logic")

    # This is the logic that would be used in the serializer validation
    def validate_future_date(date_value):
        """Simulate the validation logic from the serializer"""
        if date_value <= now:
            return False, "Session date must be in the future"
        return True, None

    # Test future date
    is_valid, error = validate_future_date(future_date)
    if is_valid:
        print(f"   ✅ Future date validation passed")
    else:
        print(f"   ❌ Future date validation failed: {error}")

    # Test past date
    is_valid, error = validate_future_date(past_date)
    if not is_valid:
        print(f"   ✅ Past date correctly rejected: {error}")
    else:
        print(f"   ❌ Past date should have been rejected")

    # Test current date
    is_valid, error = validate_future_date(current_date)
    if not is_valid:
        print(f"   ✅ Current date correctly rejected: {error}")
    else:
        print(f"   ❌ Current date should have been rejected")

    print(f"\n🎉 Date validation logic testing completed!")
    print("=" * 50)


def test_date_serialization_logic():
    """Test the date serialization logic"""
    print("\n🧪 Testing Date Serialization Logic")
    print("=" * 50)

    now = datetime.now(pytz.UTC)
    future_date = now + timedelta(days=1)

    print(f"📅 Original date: {future_date}")
    print(f"🔍 Type: {type(future_date)}")

    # Test ISO serialization
    iso_string = future_date.isoformat()
    print(f"📅 ISO string: {iso_string}")
    print(f"🔍 Type: {type(iso_string)}")

    # Test with Z suffix (common in APIs)
    iso_string_z = future_date.isoformat().replace('+00:00', 'Z')
    print(f"📅 ISO string with Z: {iso_string_z}")

    # Test parsing back
    try:
        parsed_date = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        print(f"📅 Parsed back: {parsed_date}")
        print(f"🔍 Matches original: {parsed_date == future_date}")
    except Exception as e:
        print(f"❌ Failed to parse back: {e}")

    print(f"\n🎉 Date serialization testing completed!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        test_date_validation_logic()
        test_date_serialization_logic()
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install pytz: pip install pytz")
    except Exception as e:
        print(f"❌ Test failed: {e}")
