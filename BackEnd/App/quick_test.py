#!/usr/bin/env python3
"""
Quick Notification System Test
Simple test to verify the notification system is working
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://educational-platform-production.up.railway.app"


def test_notification_system():
    print("🔔 Quick Notification System Test")
    print("=" * 40)

    # Test 1: Check if server is running
    print("\n1. Testing server connection...")
    try:
        response = requests.get(f"{BASE_URL}/api/courses/")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server returned error:", response.status_code)
            return False
    except Exception as e:
        print("❌ Cannot connect to server:", str(e))
        return False

    # Test 2: Check if notifications endpoint exists
    print("\n2. Testing notifications endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/notifications/")
        if response.status_code in [200, 401]:  # 401 is expected without auth
            print("✅ Notifications endpoint exists")
        else:
            print("❌ Notifications endpoint error:", response.status_code)
            return False
    except Exception as e:
        print("❌ Notifications endpoint error:", str(e))
        return False

    # Test 3: Check if courses endpoint exists
    print("\n3. Testing courses endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/courses/")
        if response.status_code == 200:
            print("✅ Courses endpoint exists")
            courses = response.json().get('results', [])
            print(f"   Found {len(courses)} courses")
        else:
            print("❌ Courses endpoint error:", response.status_code)
            return False
    except Exception as e:
        print("❌ Courses endpoint error:", str(e))
        return False

    # Test 4: Check if auth endpoint exists
    print("\n4. Testing auth endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login/",
                                 json={"email": "test@test.com", "password": "test"})
        # Expected for invalid credentials
        if response.status_code in [400, 401]:
            print("✅ Auth endpoint exists")
        else:
            print("❌ Auth endpoint error:", response.status_code)
            return False
    except Exception as e:
        print("❌ Auth endpoint error:", str(e))
        return False

    print("\n🎉 All basic endpoints are working!")
    print("\nNext steps:")
    print("1. Create test users (instructor and student)")
    print("2. Create a course")
    print("3. Enroll student in course")
    print("4. Send notification")
    print("5. Check if student receives notification")

    return True


if __name__ == "__main__":
    test_notification_system()
