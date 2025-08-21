#!/usr/bin/env python
"""
Simple test to send a notification directly
"""
from authentication.models import User
from notifications.views import send_notification
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()


def test_simple_notification():
    """Test sending a notification directly"""
    print("🚀 Testing Simple Notification")
    print("=" * 40)

    try:
        # Get the first user as sender
        sender = User.objects.first()
        if not sender:
            print("❌ No users found in database")
            return False

        print(f"✅ Using sender: {sender.email}")

        # Get all users as receivers
        receivers = User.objects.all()
        print(f"✅ Found {receivers.count()} users")

        # Send notification to each user
        for receiver in receivers:
            if receiver.id != sender.id:  # Don't send to self
                try:
                    notification = send_notification(
                        sender_id=sender.id,
                        receiver_id=receiver.id,
                        notification_type='announcement',
                        title='Test Notification',
                        message=f'This is a test notification sent to {receiver.first_name}!'
                    )
                    print(f"✅ Sent notification to {receiver.email}")
                except Exception as e:
                    print(f"❌ Failed to send to {receiver.email}: {e}")

        print("\n" + "=" * 40)
        print("🎉 Notification test completed!")
        print("💡 Check your frontend for real-time notifications")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_simple_notification()
