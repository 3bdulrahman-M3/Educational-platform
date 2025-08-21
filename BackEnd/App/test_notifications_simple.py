#!/usr/bin/env python3
"""
Simple Notification System Test
Tests API endpoints for notification functionality
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"


class SimpleNotificationTester:
    def __init__(self):
        self.instructor_token = None
        self.student_token = None
        self.course_id = None

    def print_step(self, step, message):
        """Print a formatted test step"""
        print(f"\n{'='*50}")
        print(f"🔔 STEP {step}: {message}")
        print(f"{'='*50}")

    def print_success(self, message):
        """Print success message"""
        print(f"✅ {message}")

    def print_error(self, message):
        """Print error message"""
        print(f"❌ {message}")

    def print_info(self, message):
        """Print info message"""
        print(f"ℹ️  {message}")

    def create_test_users(self):
        """Create test users if they don't exist"""
        self.print_info("Creating test users...")

        # Create instructor
        instructor_data = {
            "email": "test_instructor@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "Instructor",
            "role": "instructor"
        }

        # Create student
        student_data = {
            "email": "test_student@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "Student",
            "role": "student"
        }

        try:
            # Try to create instructor
            response = requests.post(
                f"{BASE_URL}/api/auth/register/", json=instructor_data)
            if response.status_code == 201:
                self.print_success("Test instructor created")
            elif response.status_code == 400 and "already exists" in response.text:
                self.print_info("Test instructor already exists")
            else:
                self.print_error(
                    f"Failed to create instructor: {response.text}")

            # Try to create student
            response = requests.post(
                f"{BASE_URL}/api/auth/register/", json=student_data)
            if response.status_code == 201:
                self.print_success("Test student created")
            elif response.status_code == 400 and "already exists" in response.text:
                self.print_info("Test student already exists")
            else:
                self.print_error(f"Failed to create student: {response.text}")

        except Exception as e:
            self.print_error(f"Error creating users: {str(e)}")

    def login_user(self, email, password, user_type):
        """Login user and get access token"""
        url = f"{BASE_URL}/api/auth/login/"
        data = {
            "email": email,
            "password": password
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                token = response.json().get('access')
                if user_type == 'instructor':
                    self.instructor_token = token
                elif user_type == 'student':
                    self.student_token = token
                self.print_success(f"{user_type.title()} login successful")
                return token
            else:
                self.print_error(
                    f"{user_type.title()} login failed: {response.text}")
                return None
        except Exception as e:
            self.print_error(f"Login error: {str(e)}")
            return None

    def create_test_course(self, instructor_token):
        """Create a test course"""
        url = f"{BASE_URL}/api/courses/create/"
        headers = {"Authorization": f"Bearer {instructor_token}"}
        data = {
            "title": f"Test Course - {datetime.now().strftime('%H:%M:%S')}",
            "description": "This is a test course for notification testing",
            "price": 99.99,
            "category": 1  # Assuming category 1 exists
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 201:
                course = response.json()
                self.course_id = course['id']
                self.print_success(
                    f"Test course created: {course['title']} (ID: {self.course_id})")
                return course
            else:
                self.print_error(f"Failed to create course: {response.text}")
                return None
        except Exception as e:
            self.print_error(f"Create course error: {str(e)}")
            return None

    def get_or_create_course(self, instructor_token):
        """Get existing course or create a new one"""
        # First try to get existing courses
        url = f"{BASE_URL}/api/courses/"
        headers = {"Authorization": f"Bearer {instructor_token}"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                courses = response.json().get('results', [])
                if courses:
                    self.course_id = courses[0]['id']
                    self.print_success(
                        f"Using existing course: {courses[0]['title']} (ID: {self.course_id})")
                    return courses[0]

            # If no courses exist, create one
            self.print_info("No courses found, creating a test course...")
            return self.create_test_course(instructor_token)

        except Exception as e:
            self.print_error(f"Get courses error: {str(e)}")
            return None

    def enroll_student(self, student_token, course_id):
        """Enroll student in course"""
        url = f"{BASE_URL}/api/courses/{course_id}/enroll/"
        headers = {"Authorization": f"Bearer {student_token}"}

        try:
            response = requests.post(url, headers=headers)
            if response.status_code == 201:
                self.print_success(f"Student enrolled in course {course_id}")
                return True
            else:
                self.print_error(f"Enrollment failed: {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Enrollment error: {str(e)}")
            return False

    def send_notification(self, instructor_token, course_id):
        """Send notification to enrolled students"""
        url = f"{BASE_URL}/api/courses/{course_id}/notify-students/"
        headers = {"Authorization": f"Bearer {instructor_token}"}
        data = {
            "title": f"Test Notification - {datetime.now().strftime('%H:%M:%S')}",
            "message": "This is a test notification sent via the notification system test script.",
            "update_type": "announcement"
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                self.print_success(f"Notification sent successfully!")
                self.print_info(
                    f"Sent to {result.get('student_count', 0)} students")
                self.print_info(
                    f"Course: {result.get('course_title', 'Unknown')}")
                return True
            else:
                self.print_error(
                    f"Failed to send notification: {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Send notification error: {str(e)}")
            return False

    def get_notifications(self, token):
        """Get user notifications"""
        url = f"{BASE_URL}/api/notifications/"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                notifications = response.json()
                self.print_success(
                    f"Retrieved {len(notifications)} notifications")
                for notif in notifications:
                    self.print_info(
                        f"- {notif['title']} ({notif['notification_type']})")
                return notifications
            else:
                self.print_error(
                    f"Failed to get notifications: {response.text}")
                return []
        except Exception as e:
            self.print_error(f"Get notifications error: {str(e)}")
            return []

    def mark_notification_read(self, token, notification_id):
        """Mark a notification as read"""
        url = f"{BASE_URL}/api/notifications/{notification_id}/mark_read/"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.patch(url, headers=headers)
            if response.status_code == 200:
                self.print_success(
                    f"Notification {notification_id} marked as read")
                return True
            else:
                self.print_error(
                    f"Failed to mark notification as read: {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Mark read error: {str(e)}")
            return False

    def run_test(self):
        """Run the complete notification test"""
        self.print_step(1, "SETTING UP TEST ENVIRONMENT")
        self.create_test_users()

        self.print_step(2, "LOGGING IN AS INSTRUCTOR")
        instructor_token = self.login_user(
            "test_instructor@example.com", "testpass123", "instructor")
        if not instructor_token:
            self.print_error("Cannot continue without instructor login")
            return False

        self.print_step(3, "LOGGING IN AS STUDENT")
        student_token = self.login_user(
            "test_student@example.com", "testpass123", "student")
        if not student_token:
            self.print_error("Cannot continue without student login")
            return False

        self.print_step(4, "SETTING UP COURSE")
        course = self.get_or_create_course(instructor_token)
        if not course:
            self.print_error("Cannot continue without a course")
            return False

        self.print_step(5, "ENROLLING STUDENT IN COURSE")
        if not self.enroll_student(student_token, self.course_id):
            self.print_error("Cannot continue without enrollment")
            return False

        self.print_step(6, "SENDING NOTIFICATION")
        if not self.send_notification(instructor_token, self.course_id):
            self.print_error("Failed to send notification")
            return False

        self.print_step(7, "CHECKING STUDENT NOTIFICATIONS")
        notifications = self.get_notifications(student_token)

        if notifications:
            self.print_step(8, "TESTING MARK AS READ")
            # Mark the first notification as read
            if notifications:
                self.mark_notification_read(
                    student_token, notifications[0]['id'])

                # Check notifications again to verify read status
                updated_notifications = self.get_notifications(student_token)
                if updated_notifications and updated_notifications[0]['is_read']:
                    self.print_success("Mark as read functionality working!")
                else:
                    self.print_error("Mark as read functionality failed")

        self.print_step(9, "TEST SUMMARY")
        self.print_info(f"Course ID: {self.course_id}")
        self.print_info(f"Notifications sent: 1")
        self.print_info(f"Notifications received: {len(notifications)}")

        if notifications:
            self.print_success("🎉 NOTIFICATION SYSTEM TEST PASSED!")
            self.print_info("API functionality is working correctly")
            return True
        else:
            self.print_error("❌ NOTIFICATION SYSTEM TEST FAILED!")
            return False


def main():
    """Main test function"""
    print("🔔 SIMPLE NOTIFICATION SYSTEM TEST")
    print("=" * 50)

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/courses/")
        if response.status_code != 200:
            print("❌ Server is not running or not accessible")
            print(
                "Please start the server with: daphne -b 0.0.0.0 -p 8000 App.asgi:application")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print(
            "Please start the server with: daphne -b 0.0.0.0 -p 8000 App.asgi:application")
        return

    # Run the test
    tester = SimpleNotificationTester()
    success = tester.run_test()

    if success:
        print("\n🎉 Test passed! The notification system API is working correctly.")
        print("Next step: Test WebSocket functionality for real-time notifications.")
    else:
        print("\n❌ Test failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
