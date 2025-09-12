#!/usr/bin/env python
"""
Script to reset and fix migration state for the chat system
"""
import os
import shutil
from pathlib import Path

def reset_migrations():
    print("🔄 Resetting migration state...")
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Apps to reset
    apps_to_reset = ['authentication', 'chat']
    
    for app_name in apps_to_reset:
        migrations_dir = current_dir / app_name / 'migrations'
        
        if migrations_dir.exists():
            print(f"\n📁 Processing {app_name} migrations...")
            
            # Keep __init__.py and delete all other migration files
            init_file = migrations_dir / '__init__.py'
            if init_file.exists():
                # Create a backup
                backup_dir = migrations_dir / 'backup'
                backup_dir.mkdir(exist_ok=True)
                
                # Move all migration files except __init__.py to backup
                for file in migrations_dir.glob('*.py'):
                    if file.name != '__init__.py':
                        shutil.move(str(file), str(backup_dir / file.name))
                        print(f"   📦 Backed up {file.name}")
            
            print(f"   ✅ {app_name} migrations reset")
    
    print("\n🎯 Next steps:")
    print("1. Run: python manage.py makemigrations")
    print("2. Run: python manage.py migrate")
    print("3. Run: python manage.py migrate chat")

if __name__ == "__main__":
    reset_migrations()

