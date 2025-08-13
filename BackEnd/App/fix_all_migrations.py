#!/usr/bin/env python
"""
Comprehensive script to fix all database migration issues
"""
from django.db.migrations.executor import MigrationExecutor
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


def check_migration_status():
    """Check the current migration status"""
    print("🔍 Checking migration status...")

    with connection.cursor() as cursor:
        # Check if migration tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'django_migrations'
        """)
        if not cursor.fetchone():
            print("❌ Django migrations table doesn't exist")
            return False

        # Check courses table structure
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'courses_course'
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"📋 Current courses_course columns: {columns}")

        # Check enrollment table structure
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'courses_enrollment'
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"📋 Current courses_enrollment columns: {columns}")

        return True


def fix_database_structure():
    """Fix the database structure by adding missing columns"""
    print("\n🔧 Fixing database structure...")

    with connection.cursor() as cursor:
        try:
            # Check and add instructor_id to courses_course
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'courses_course' 
                AND column_name = 'instructor_id'
            """)
            if not cursor.fetchone():
                print("➕ Adding instructor_id to courses_course...")
                cursor.execute("""
                    ALTER TABLE courses_course 
                    ADD COLUMN instructor_id INTEGER REFERENCES auth_user(id)
                """)
                print("✅ Added instructor_id column")
            else:
                print("✅ instructor_id column already exists")

            # Check and add missing columns to courses_enrollment
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'courses_enrollment' 
                AND column_name = 'withdrawn_at'
            """)
            if not cursor.fetchone():
                print("➕ Adding withdrawn_at to courses_enrollment...")
                cursor.execute("""
                    ALTER TABLE courses_enrollment 
                    ADD COLUMN withdrawn_at TIMESTAMP NULL
                """)
                print("✅ Added withdrawn_at column")
            else:
                print("✅ withdrawn_at column already exists")

            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'courses_enrollment' 
                AND column_name = 'is_active'
            """)
            if not cursor.fetchone():
                print("➕ Adding is_active to courses_enrollment...")
                cursor.execute("""
                    ALTER TABLE courses_enrollment 
                    ADD COLUMN is_active BOOLEAN DEFAULT TRUE
                """)
                print("✅ Added is_active column")
            else:
                print("✅ is_active column already exists")

            # Check and add missing columns to courses_course
            missing_columns = [
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('image', 'VARCHAR(255) NULL')
            ]

            for col_name, col_type in missing_columns:
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'courses_course' 
                    AND column_name = '{col_name}'
                """)
                if not cursor.fetchone():
                    print(f"➕ Adding {col_name} to courses_course...")
                    cursor.execute(f"""
                        ALTER TABLE courses_course 
                        ADD COLUMN {col_name} {col_type}
                    """)
                    print(f"✅ Added {col_name} column")
                else:
                    print(f"✅ {col_name} column already exists")

            print("✅ Database structure fixed successfully!")

        except Exception as e:
            print(f"❌ Error fixing database structure: {e}")
            return False

    return True


def reset_migrations():
    """Reset migrations and recreate them"""
    print("\n🔄 Resetting migrations...")

    try:
        # Remove existing migration files (except __init__.py)
        import glob
        migration_files = glob.glob("courses/migrations/0*.py")
        for file in migration_files:
            os.remove(file)
            print(f"🗑️ Removed {file}")

        # Remove migration records from database
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM django_migrations WHERE app = 'courses'")
            print("🗑️ Removed courses migration records from database")

        # Create fresh migrations
        execute_from_command_line(['manage.py', 'makemigrations', 'courses'])
        print("✅ Created fresh migrations")

        # Apply migrations
        execute_from_command_line(['manage.py', 'migrate', 'courses'])
        print("✅ Applied fresh migrations")

    except Exception as e:
        print(f"❌ Error resetting migrations: {e}")
        return False

    return True


def test_database():
    """Test the database by creating sample data"""
    print("\n🧪 Testing database...")

    try:
        from authentication.models import User
        from courses.models import Course, Enrollment

        # Create test instructor
        instructor = User.objects.create_user(
            email='test_instructor@test.com',
            username='test_instructor',
            password='testpass123',
            role='instructor',
            first_name='Test',
            last_name='Instructor'
        )
        print(f"✅ Created test instructor: {instructor.email}")

        # Create test course
        course = Course.objects.create(
            title='Test Course',
            description='This is a test course',
            instructor=instructor
        )
        print(f"✅ Created test course: {course.title}")

        # Create test student
        student = User.objects.create_user(
            email='test_student@test.com',
            username='test_student',
            password='testpass123',
            role='student',
            first_name='Test',
            last_name='Student'
        )
        print(f"✅ Created test student: {student.email}")

        # Create test enrollment
        enrollment = Enrollment.objects.create(
            student=student,
            course=course
        )
        print(f"✅ Created test enrollment")

        # Test queries
        courses = Course.objects.all()
        print(f"✅ Retrieved {courses.count()} courses")

        enrollments = Enrollment.objects.all()
        print(f"✅ Retrieved {enrollments.count()} enrollments")

        # Clean up
        enrollment.delete()
        course.delete()
        student.delete()
        instructor.delete()
        print("✅ Cleaned up test data")

        return True

    except Exception as e:
        print(f"❌ Error testing database: {e}")
        return False


def main():
    """Main function to fix all migration issues"""
    print("🚀 Starting comprehensive migration fix...")

    # Step 1: Check current status
    if not check_migration_status():
        print("❌ Migration system not properly set up")
        return

    # Step 2: Fix database structure
    if not fix_database_structure():
        print("❌ Failed to fix database structure")
        return

    # Step 3: Reset migrations if needed
    print("\n🤔 Do you want to reset migrations? (This will recreate all migration files)")
    response = input(
        "Enter 'yes' to reset migrations, or press Enter to skip: ")

    if response.lower() == 'yes':
        if not reset_migrations():
            print("❌ Failed to reset migrations")
            return

    # Step 4: Test the database
    if not test_database():
        print("❌ Database test failed")
        return

    print("\n🎉 All migration issues fixed successfully!")
    print("✅ Database structure is correct")
    print("✅ All required columns exist")
    print("✅ Sample data can be created and retrieved")
    print("\n🚀 You can now start your Django server and test the APIs!")


if __name__ == "__main__":
    main()
