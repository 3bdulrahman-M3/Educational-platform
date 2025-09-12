#!/usr/bin/env python
"""
Script to fix migration conflicts and apply chat migrations
"""
import os
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()

def fix_migrations():
    print("🔧 Fixing migration conflicts...")
    
    try:
        # First, let's see what migrations are pending
        print("\n1. Checking migration status...")
        os.system("python manage.py showmigrations")
        
        # Try to fake apply the problematic migration
        print("\n2. Marking problematic migration as applied...")
        os.system("python manage.py migrate authentication 0005 --fake")
        
        # Now try to apply chat migrations
        print("\n3. Applying chat migrations...")
        os.system("python manage.py migrate chat")
        
        # Apply any remaining migrations
        print("\n4. Applying remaining migrations...")
        os.system("python manage.py migrate")
        
        print("\n✅ Migration fix completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTry running these commands manually:")
        print("python manage.py migrate authentication 0005 --fake")
        print("python manage.py migrate chat")
        print("python manage.py migrate")

if __name__ == "__main__":
    fix_migrations()

