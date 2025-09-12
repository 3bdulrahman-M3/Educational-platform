#!/usr/bin/env python
"""
Create test data for chat system
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()

from django.contrib.auth import get_user_model
from chat.models import Conversation, Message

User = get_user_model()

def create_test_data():
    print("🧪 Creating test data for chat system...")
    
    # Create test users
    try:
        # Get or create admin user
        try:
            admin_user = User.objects.get(email='admin@test.com')
            print("ℹ️ Admin user already exists")
        except User.DoesNotExist:
            admin_user = User.objects.create_user(
                email='admin@test.com',
                username='testadmin',
                first_name='Admin',
                last_name='User',
                role='admin',
                password='admin123'
            )
            print("✅ Admin user created")
        
        # Get or create test student
        try:
            student_user = User.objects.get(email='student@test.com')
            print("ℹ️ Student user already exists")
        except User.DoesNotExist:
            student_user = User.objects.create_user(
                email='student@test.com',
                username='teststudent',
                first_name='Test',
                last_name='Student',
                role='student',
                password='student123'
            )
            print("✅ Student user created")
        
        # Create conversation
        conversation, created = Conversation.objects.get_or_create(
            user=student_user,
            defaults={'is_active': True}
        )
        if created:
            print("✅ Conversation created")
        else:
            print("ℹ️ Conversation already exists")
        
        # Create test messages
        if not Message.objects.filter(conversation=conversation).exists():
            # Student message
            Message.objects.create(
                conversation=conversation,
                sender=student_user,
                content="Hello admin, I need help with my course!",
                message_type='text'
            )
            
            # Admin message
            Message.objects.create(
                conversation=conversation,
                sender=admin_user,
                content="Hi! I'm here to help. What's the issue?",
                message_type='text'
            )
            
            # Another student message
            Message.objects.create(
                conversation=conversation,
                sender=student_user,
                content="I can't access the video lessons. It shows an error.",
                message_type='text'
            )
            
            print("✅ Test messages created")
        else:
            print("ℹ️ Test messages already exist")
        
        print("\n🎉 Test data setup completed!")
        print("\n📝 Test Credentials:")
        print("Admin: admin@test.com / admin123")
        print("Student: student@test.com / student123")
        print(f"\n💬 Conversation ID: {conversation.id}")
        print(f"📊 Total conversations: {Conversation.objects.count()}")
        print(f"📨 Total messages: {Message.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")

if __name__ == "__main__":
    create_test_data()
