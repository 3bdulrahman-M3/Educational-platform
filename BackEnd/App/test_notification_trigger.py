#!/usr/bin/env python
"""
Test script to trigger a real notification and verify the complete flow
"""
import requests
import json
import time


def test_notification_flow():
    """Test the complete notification flow"""
    print("🚀 Testing Complete Notification Flow")
    print("=" * 50)

    # Step 1: Login to get a token
    print("1️⃣ Logging in...")
    login_data = {
        "email": "youssefabdelmaged50@gmail.com",
        "password": "123456"
    }

    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/auth/login/',
            json=login_data
        )

        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        data = response.json()
        token = data.get('access')
        print(f"✅ Login successful, got token: {token[:20]}...")

    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

    # Step 2: Send a test notification
    print("\n2️⃣ Sending test notification...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    notification_data = {
        "receiver_id": 1,  # Send to user ID 1
        "message": "🎉 Test notification from backend!",
        "notification_type": "announcement"
    }

    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/notifications/send/',
            json=notification_data,
            headers=headers
        )

        if response.status_code == 200:
            print("✅ Test notification sent successfully!")
        else:
            print(f"❌ Failed to send notification: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error sending notification: {e}")

    # Step 3: Check notifications
    print("\n3️⃣ Checking notifications...")
    try:
        response = requests.get(
            'http://127.0.0.1:8000/api/notifications/',
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            notifications = data.get('results', data)
            print(f"✅ Found {len(notifications)} notifications")

            for notif in notifications[:3]:  # Show first 3
                print(f"   📨 {notif.get('message', 'No message')}")
        else:
            print(f"❌ Failed to get notifications: {response.status_code}")

    except Exception as e:
        print(f"❌ Error getting notifications: {e}")

    print("\n" + "=" * 50)
    print("🎉 Notification system test completed!")
    print("💡 Check your frontend - you should see:")
    print("   - Green WiFi icon (connected)")
    print("   - Real-time notification delivery")
    print("   - Notification bell with count")

    return True


if __name__ == "__main__":
    test_notification_flow()
