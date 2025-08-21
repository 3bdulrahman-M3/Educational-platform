#!/usr/bin/env python
"""
Test script to trigger automatic notifications
"""
import requests
import json
import time


def test_automatic_notifications():
    """Test automatic notifications by creating a course and enrolling"""
    print("🚀 Testing Automatic Notifications")
    print("=" * 50)

    # Step 1: Login as instructor
    print("1️⃣ Logging in as instructor...")
    instructor_login = {
        "email": "youssefabdelmaged50@gmail.com",
        "password": "123456"
    }

    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/auth/login/',
            json=instructor_login
        )

        if response.status_code != 200:
            print(f"❌ Instructor login failed: {response.status_code}")
            return False

        instructor_data = response.json()
        instructor_token = instructor_data.get('tokens', {}).get('access')
        print(f"✅ Instructor login successful")

    except Exception as e:
        print(f"❌ Instructor login error: {e}")
        return False

    # Step 2: Create a course (should trigger notifications to all students)
    print("\n2️⃣ Creating a course...")
    headers = {
        'Authorization': f'Bearer {instructor_token}',
        'Content-Type': 'application/json'
    }

    course_data = {
        "title": "Test Course for Notifications",
        "description": "This course is created to test automatic notifications",
        "price": 99.99,
        "category": 1  # Assuming category 1 exists
    }

    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/courses/',
            json=course_data,
            headers=headers
        )

        if response.status_code == 201:
            course = response.json()
            course_id = course.get('id')
            print(f"✅ Course created successfully: {course['title']}")
        else:
            print(f"❌ Failed to create course: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error creating course: {e}")
        return False

    # Step 3: Login as student
    print("\n3️⃣ Logging in as student...")
    student_login = {
        "email": "meagmeg8@gmail.com",  # Use a different student email
        "password": "123456"
    }

    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/auth/login/',
            json=student_login
        )

        if response.status_code != 200:
            print(f"❌ Student login failed: {response.status_code}")
            return False

        student_data = response.json()
        student_token = student_data.get('tokens', {}).get('access')
        print(f"✅ Student login successful")

    except Exception as e:
        print(f"❌ Student login error: {e}")
        return False

    # Step 4: Enroll student in course (should trigger notification to instructor)
    print(f"\n4️⃣ Enrolling student in course {course_id}...")
    student_headers = {
        'Authorization': f'Bearer {student_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            f'http://127.0.0.1:8000/api/courses/{course_id}/enroll/',
            headers=student_headers
        )

        if response.status_code == 201:
            print("✅ Student enrolled successfully")
        else:
            print(f"❌ Failed to enroll: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error enrolling: {e}")

    # Step 5: Update course (should trigger notifications to enrolled students)
    print(f"\n5️⃣ Updating course...")
    update_data = {
        "description": "Updated description to test notifications"
    }

    try:
        response = requests.put(
            f'http://127.0.0.1:8000/api/courses/{course_id}/',
            json=update_data,
            headers=headers
        )

        if response.status_code == 200:
            print("✅ Course updated successfully")
        else:
            print(f"❌ Failed to update course: {response.status_code}")

    except Exception as e:
        print(f"❌ Error updating course: {e}")

    # Step 6: Check notifications for both users
    print(f"\n6️⃣ Checking notifications...")

    # Check instructor notifications
    try:
        response = requests.get(
            'http://127.0.0.1:8000/api/notifications/',
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            instructor_notifications = data.get('results', data)
            print(
                f"📨 Instructor has {len(instructor_notifications)} notifications")

            for notif in instructor_notifications[:3]:
                print(
                    f"   - {notif.get('title', 'No title')}: {notif.get('message', 'No message')}")
        else:
            print(
                f"❌ Failed to get instructor notifications: {response.status_code}")

    except Exception as e:
        print(f"❌ Error getting instructor notifications: {e}")

    # Check student notifications
    try:
        response = requests.get(
            'http://127.0.0.1:8000/api/notifications/',
            headers=student_headers
        )

        if response.status_code == 200:
            data = response.json()
            student_notifications = data.get('results', data)
            print(f"📨 Student has {len(student_notifications)} notifications")

            for notif in student_notifications[:3]:
                print(
                    f"   - {notif.get('title', 'No title')}: {notif.get('message', 'No message')}")
        else:
            print(
                f"❌ Failed to get student notifications: {response.status_code}")

    except Exception as e:
        print(f"❌ Error getting student notifications: {e}")

    print("\n" + "=" * 50)
    print("🎉 Automatic notification test completed!")
    print("💡 Check your frontend - you should see:")
    print("   - Real-time notifications appearing")
    print("   - Notification bell with count")
    print("   - Green WiFi icon (connected)")

    return True


if __name__ == "__main__":
    test_automatic_notifications()
