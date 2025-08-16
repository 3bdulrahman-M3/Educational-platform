#!/usr/bin/env python
"""
Basic test script to test date functionality using only standard library
"""

from datetime import datetime, timedelta


def test_date_functionality():
    """Test basic date functionality"""
    print("🧪 Testing Basic Date Functionality")
    print("=" * 50)

    # Create test dates
    now = datetime.now()
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

    # Test 6: Date comparison logic (simulating serializer validation)
    print(f"\n🔍 Test 6: Date comparison logic (Serializer Simulation)")

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

    # Test 7: Date serialization logic
    print(f"\n🔍 Test 7: Date serialization logic")

    print(f"📅 Original date: {future_date}")
    print(f"🔍 Type: {type(future_date)}")

    # Test ISO serialization
    iso_string = future_date.isoformat()
    print(f"📅 ISO string: {iso_string}")
    print(f"🔍 Type: {type(iso_string)}")

    # Test parsing back
    try:
        parsed_date = datetime.fromisoformat(iso_string)
        print(f"📅 Parsed back: {parsed_date}")
        print(f"🔍 Matches original: {parsed_date == future_date}")
    except Exception as e:
        print(f"❌ Failed to parse back: {e}")

    # Test 8: Different date formats
    print(f"\n🔍 Test 8: Different date formats")

    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d'
    ]

    for fmt in formats:
        try:
            formatted_date = future_date.strftime(fmt)
            print(f"   📅 Format '{fmt}': {formatted_date}")
        except Exception as e:
            print(f"   ❌ Format '{fmt}' failed: {e}")

    print(f"\n🎉 Basic date functionality testing completed!")
    print("=" * 50)


def test_serializer_logic_simulation():
    """Simulate the serializer logic for date handling"""
    print("\n🧪 Testing Serializer Logic Simulation")
    print("=" * 50)

    now = datetime.now()
    future_date = now + timedelta(days=1)

    # Simulate the SessionCreateSerializer validation
    class MockSessionCreateSerializer:
        def __init__(self, data, context=None):
            self.data = data
            self.context = context or {}
            self.errors = {}

        def validate_date(self, value):
            """Simulate the date validation from the serializer"""
            if value <= now:
                raise ValueError("Session date must be in the future")
            return value

        def is_valid(self):
            """Simulate validation check"""
            try:
                if 'date' in self.data:
                    # Convert string to datetime if needed
                    if isinstance(self.data['date'], str):
                        try:
                            date_value = datetime.fromisoformat(
                                self.data['date'].replace('Z', '+00:00'))
                        except:
                            date_value = datetime.fromisoformat(
                                self.data['date'])
                    else:
                        date_value = self.data['date']

                    self.validate_date(date_value)
                return True
            except Exception as e:
                self.errors['date'] = str(e)
                return False

    # Test valid data
    print("🔍 Test 1: Valid future date")
    valid_data = {
        'title': 'Test Session',
        'description': 'Test Description',
        'date': future_date.isoformat(),
        'max_participants': 5
    }

    serializer = MockSessionCreateSerializer(valid_data)
    if serializer.is_valid():
        print("   ✅ Valid future date accepted")
    else:
        print(f"   ❌ Valid future date rejected: {serializer.errors}")

    # Test invalid data (past date)
    print("\n🔍 Test 2: Invalid past date")
    invalid_data = {
        'title': 'Test Session',
        'description': 'Test Description',
        'date': (now - timedelta(days=1)).isoformat(),
        'max_participants': 5
    }

    serializer = MockSessionCreateSerializer(invalid_data)
    if not serializer.is_valid():
        print(
            f"   ✅ Invalid past date correctly rejected: {serializer.errors}")
    else:
        print("   ❌ Invalid past date should have been rejected")

    # Test current date
    print("\n🔍 Test 3: Current date")
    current_data = {
        'title': 'Test Session',
        'description': 'Test Description',
        'date': now.isoformat(),
        'max_participants': 5
    }

    serializer = MockSessionCreateSerializer(current_data)
    if not serializer.is_valid():
        print(f"   ✅ Current date correctly rejected: {serializer.errors}")
    else:
        print("   ❌ Current date should have been rejected")

    print(f"\n🎉 Serializer logic simulation completed!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        test_date_functionality()
        test_serializer_logic_simulation()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
