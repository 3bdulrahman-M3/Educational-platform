#!/usr/bin/env python
"""
Quick fix script to add missing database columns
"""
from django.db import connection
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()


def quick_fix():
    """Quick fix for missing database columns"""
    print("🔧 Quick fixing database columns...")

    with connection.cursor() as cursor:
        try:
            # Fix courses_course table
            print("📋 Fixing courses_course table...")

            # Add instructor_id if missing
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
                print("✅ Added instructor_id")

            # Add created_at if missing
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'courses_course' 
                AND column_name = 'created_at'
            """)
            if not cursor.fetchone():
                print("➕ Adding created_at to courses_course...")
                cursor.execute("""
                    ALTER TABLE courses_course 
                    ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """)
                print("✅ Added created_at")

            # Add updated_at if missing
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'courses_course' 
                AND column_name = 'updated_at'
            """)
            if not cursor.fetchone():
                print("➕ Adding updated_at to courses_course...")
                cursor.execute("""
                    ALTER TABLE courses_course 
                    ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """)
                print("✅ Added updated_at")

            # Add image if missing
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'courses_course' 
                AND column_name = 'image'
            """)
            if not cursor.fetchone():
                print("➕ Adding image to courses_course...")
                cursor.execute("""
                    ALTER TABLE courses_course 
                    ADD COLUMN image VARCHAR(255) NULL
                """)
                print("✅ Added image")

            # Fix courses_enrollment table
            print("📋 Fixing courses_enrollment table...")

            # Add withdrawn_at if missing
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
                print("✅ Added withdrawn_at")

            # Add is_active if missing
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
                print("✅ Added is_active")

            print("\n✅ All database columns fixed successfully!")
            print("🚀 You can now start your Django server!")

        except Exception as e:
            print(f"❌ Error fixing database: {e}")
            return False

    return True


if __name__ == "__main__":
    quick_fix()
