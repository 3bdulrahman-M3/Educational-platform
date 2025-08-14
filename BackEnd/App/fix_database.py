#!/usr/bin/env python
"""
Script to fix database issues and test registration
"""
from django.db import connection
from django.core.management import execute_from_command_line
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()


def fix_database():
    """Fix database issues"""
    print("🔧 Fixing database issues...")

    # Run migrations
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        print("✅ Made migrations successfully")
    except Exception as e:
        print(f"❌ Error making migrations: {e}")

    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Applied migrations successfully")
    except Exception as e:
        print(f"❌ Error applying migrations: {e}")

    # Check if the withdrawn_at column exists
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'courses_enrollment' 
                AND column_name = 'withdrawn_at'
            """)
            result = cursor.fetchone()
            if result:
                print("✅ withdrawn_at column exists")
            else:
                print("❌ withdrawn_at column missing - adding it manually")
                cursor.execute("""
                    ALTER TABLE courses_enrollment 
                    ADD COLUMN withdrawn_at TIMESTAMP NULL
                """)
                cursor.execute("""
                    ALTER TABLE courses_enrollment 
                    ADD COLUMN is_active BOOLEAN DEFAULT TRUE
                """)
                print("✅ Added missing columns manually")
        except Exception as e:
            print(f"❌ Error checking/adding columns: {e}")


def test_registration():
    """Test user registration"""
    print("\n🧪 Testing user registration...")

    from authentication.models import User

    # Test data
    test_user_data = {
        'email': 'test_instructor@test.com',
        'username': 'test_instructor',
        'password': 'testpass123',
        'role': 'instructor',
        'first_name': 'Test',
        'last_name': 'Instructor'
    }

    try:
        # Create user
        user = User.objects.create_user(**test_user_data)
        print(f"✅ User created successfully")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Username: {user.username}")

        # Verify role
        if user.role == 'instructor':
            print("✅ Role is correctly set to instructor")
        else:
            print(f"❌ Role is {user.role}, expected instructor")

        # Clean up
        user.delete()
        print("✅ Test user deleted")

    except Exception as e:
        print(f"❌ Error creating test user: {e}")


if __name__ == "__main__":
    print("🚀 Starting database fix and test...")
    fix_database()
    test_registration()
    print("\n🎉 Database fix and test completed!")
