#!/usr/bin/env python3
"""
Simple One-Command Test for Notification System
Run this to quickly verify everything is working
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"


def test_notification_system():
    print("🔔 TESTING NOTIFICATION SYSTEM NOW")
    print("=" * 50)

    # Test 1: Check server
    print("\n1️⃣ Testing server connection...")
    try:
        response = requests.get(f"{BASE_URL}/api/courses/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print("💡 Please start the server with: python manage.py runserver 8000")
        return False

    # Test 2: Check notifications endpoint
    print("\n2️⃣ Testing notifications endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/notifications/", timeout=5)
        if response.status_code in [200, 401]:  # 401 is expected without auth
            print("✅ Notifications endpoint exists!")
        else:
            print(f"❌ Notifications endpoint error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Notifications endpoint error: {str(e)}")
        return False

    # Test 3: Create test users
    print("\n3️⃣ Creating test users...")

    # Create instructor
    instructor_data = {
        "email": f"test_instructor_{int(time.time())}@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "Instructor",
        "role": "instructor"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register/", json=instructor_data, timeout=10)
        if response.status_code == 201:
            print("✅ Test instructor created!")
        else:
            print(f"❌ Failed to create instructor: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating instructor: {str(e)}")
        return False

    # Create student
    student_data = {
        "email": f"test_student_{int(time.time())}@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "Student",
        "role": "student"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register/", json=student_data, timeout=10)
        if response.status_code == 201:
            print("✅ Test student created!")
        else:
            print(f"❌ Failed to create student: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating student: {str(e)}")
        return False

    # Test 4: Login users
    print("\n4️⃣ Logging in users...")

    # Login instructor
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login/",
                                 json={
                                     "email": instructor_data["email"], "password": "testpass123"},
                                 timeout=10)
        if response.status_code == 200:
            instructor_token = response.json().get('access')
            print("✅ Instructor logged in!")
        else:
            print(f"❌ Instructor login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Instructor login error: {str(e)}")
        return False

    # Login student
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login/",
                                 json={
                                     "email": student_data["email"], "password": "testpass123"},
                                 timeout=10)
        if response.status_code == 200:
            student_token = response.json().get('access')
            print("✅ Student logged in!")
        else:
            print(f"❌ Student login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Student login error: {str(e)}")
        return False

    # Test 5: Create course
    print("\n5️⃣ Creating test course...")
    course_data = {
        "title": f"Test Course - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Test course for notification system",
        "price": 99.99,
        "category": 1
    }

    try:
        response = requests.post(f"{BASE_URL}/api/courses/create/",
                                 json=course_data,
                                 headers={
                                     "Authorization": f"Bearer {instructor_token}"},
                                 timeout=10)
        if response.status_code == 201:
            course = response.json()
            course_id = course['id']
            print(f"✅ Test course created! (ID: {course_id})")
        else:
            print(f"❌ Failed to create course: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating course: {str(e)}")
        return False

    # Test 6: Enroll student
    print("\n6️⃣ Enrolling student in course...")
    try:
        response = requests.post(f"{BASE_URL}/api/courses/{course_id}/enroll/",
                                 headers={
                                     "Authorization": f"Bearer {student_token}"},
                                 timeout=10)
        if response.status_code == 201:
            print("✅ Student enrolled in course!")
        else:
            print(f"❌ Enrollment failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Enrollment error: {str(e)}")
        return False

    # Test 7: Send notification
    print("\n7️⃣ Sending test notification...")
    notification_data = {
        "title": f"Test Notification - {datetime.now().strftime('%H:%M:%S')}",
        "message": "This is a test notification from the automated test!",
        "update_type": "announcement"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/courses/{course_id}/notify-students/",
                                 json=notification_data,
                                 headers={
                                     "Authorization": f"Bearer {instructor_token}"},
                                 timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Notification sent successfully!")
            print(f"   📧 Sent to {result.get('student_count', 0)} students")
            print(f"   📚 Course: {result.get('course_title', 'Unknown')}")
        else:
            print(f"❌ Failed to send notification: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending notification: {str(e)}")
        return False

    # Test 8: Check student notifications
    print("\n8️⃣ Checking student notifications...")
    try:
        response = requests.get(f"{BASE_URL}/api/notifications/",
                                headers={
                                    "Authorization": f"Bearer {student_token}"},
                                timeout=10)
        if response.status_code == 200:
            notifications = response.json()
            if notifications:
                print(
                    f"✅ Student received {len(notifications)} notification(s)!")
                for notif in notifications:
                    print(
                        f"   📬 {notif['title']} ({notif['notification_type']})")
            else:
                print("❌ No notifications found for student")
                return False
        else:
            print(f"❌ Failed to get notifications: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting notifications: {str(e)}")
        return False

    # Success!
    print("\n" + "=" * 50)
    print("🎉 NOTIFICATION SYSTEM TEST PASSED!")
    print("=" * 50)
    print("✅ All components are working correctly:")
    print("   • Server is running")
    print("   • User authentication works")
    print("   • Course creation works")
    print("   • Student enrollment works")
    print("   • Notification sending works")
    print("   • Notification retrieval works")
    print("\n🚀 The notification system is fully functional!")
    print("\nNext steps:")
    print("1. Test the frontend notification bell")
    print("2. Test WebSocket real-time notifications")
    print("3. Test with multiple students")

    return True


if __name__ == "__main__":
    try:
        success = test_notification_system()
        if not success:
            print("\n❌ Test failed. Check the error messages above.")
            print("💡 Make sure the server is running: python manage.py runserver 8000")
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        print("💡 Check server logs for more details")
