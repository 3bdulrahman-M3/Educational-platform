#!/usr/bin/env python3
"""
Comprehensive Notification System Test
Tests both API endpoints and WebSocket functionality
"""

import requests
import json
import time
import websocket
import threading
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/notifications/"


class NotificationTester:
    def __init__(self):
        self.access_token = None
        self.instructor_token = None
        self.student_token = None
        self.course_id = None
        self.notifications_received = []
        self.ws_connected = False

    def print_step(self, step, message):
        """Print a formatted test step"""
        print(f"\n{'='*60}")
        print(f"🔔 STEP {step}: {message}")
        print(f"{'='*60}")

    def print_success(self, message):
        """Print success message"""
        print(f"✅ {message}")

    def print_error(self, message):
        """Print error message"""
        print(f"❌ {message}")

    def print_info(self, message):
        """Print info message"""
        print(f"ℹ️  {message}")

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

    def get_courses(self, token):
        """Get available courses"""
        url = f"{BASE_URL}/api/courses/"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                courses = response.json().get('results', [])
                if courses:
                    self.course_id = courses[0]['id']
                    self.print_success(
                        f"Found course: {courses[0]['title']} (ID: {self.course_id})")
                    return courses[0]
                else:
                    self.print_error("No courses found")
                    return None
            else:
                self.print_error(f"Failed to get courses: {response.text}")
                return None
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

    def on_ws_message(self, ws, message):
        """Handle WebSocket messages"""
        try:
            data = json.loads(message)
            self.print_info(
                f"WebSocket message received: {data.get('type', 'unknown')}")
            if data.get('type') == 'notification':
                self.notifications_received.append(
                    data.get('notification', {}))
                self.print_success(
                    f"Real-time notification: {data['notification']['title']}")
        except Exception as e:
            self.print_error(f"WebSocket message error: {str(e)}")

    def on_ws_open(self, ws):
        """Handle WebSocket connection open"""
        self.ws_connected = True
        self.print_success("WebSocket connected!")

        # Send authentication
        auth_message = {
            "type": "auth",
            "token": self.student_token
        }
        ws.send(json.dumps(auth_message))
        self.print_info("Authentication sent to WebSocket")

    def on_ws_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close"""
        self.ws_connected = False
        self.print_info("WebSocket disconnected")

    def on_ws_error(self, ws, error):
        """Handle WebSocket errors"""
        self.print_error(f"WebSocket error: {str(error)}")

    def test_websocket(self, token):
        """Test WebSocket connection and real-time notifications"""
        self.print_info("Starting WebSocket test...")

        # Create WebSocket connection
        ws = websocket.WebSocketApp(
            WS_URL,
            on_open=self.on_ws_open,
            on_message=self.on_ws_message,
            on_close=self.on_ws_close,
            on_error=self.on_ws_error
        )

        # Start WebSocket in a separate thread
        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()

        # Wait for connection
        time.sleep(2)

        if self.ws_connected:
            self.print_success("WebSocket test completed successfully")
            return True
        else:
            self.print_error("WebSocket connection failed")
            return False

    def run_comprehensive_test(self):
        """Run the complete notification system test"""
        self.print_step(1, "INITIALIZING NOTIFICATION SYSTEM TEST")
        self.print_info(
            "Testing both API endpoints and WebSocket functionality")

        # Step 2: Login as instructor
        self.print_step(2, "LOGGING IN AS INSTRUCTOR")
        instructor_token = self.login_user(
            "instructor@test.com", "testpass123", "instructor")
        if not instructor_token:
            self.print_error("Cannot continue without instructor login")
            return False

        # Step 3: Login as student
        self.print_step(3, "LOGGING IN AS STUDENT")
        student_token = self.login_user(
            "student@test.com", "testpass123", "student")
        if not student_token:
            self.print_error("Cannot continue without student login")
            return False

        # Step 4: Get available courses
        self.print_step(4, "GETTING AVAILABLE COURSES")
        course = self.get_courses(instructor_token)
        if not course:
            self.print_error("Cannot continue without a course")
            return False

        # Step 5: Enroll student in course
        self.print_step(5, "ENROLLING STUDENT IN COURSE")
        if not self.enroll_student(student_token, self.course_id):
            self.print_error("Cannot continue without enrollment")
            return False

        # Step 6: Test WebSocket connection
        self.print_step(6, "TESTING WEBSOCKET CONNECTION")
        if not self.test_websocket(student_token):
            self.print_error("WebSocket test failed")
            return False

        # Step 7: Send notification
        self.print_step(7, "SENDING NOTIFICATION")
        if not self.send_notification(instructor_token, self.course_id):
            self.print_error("Failed to send notification")
            return False

        # Step 8: Wait for real-time notification
        self.print_step(8, "WAITING FOR REAL-TIME NOTIFICATION")
        self.print_info("Waiting 5 seconds for WebSocket notification...")
        time.sleep(5)

        # Step 9: Check notifications via API
        self.print_step(9, "CHECKING NOTIFICATIONS VIA API")
        notifications = self.get_notifications(student_token)

        # Step 10: Summary
        self.print_step(10, "TEST SUMMARY")
        self.print_info(f"WebSocket connected: {self.ws_connected}")
        self.print_info(
            f"Real-time notifications received: {len(self.notifications_received)}")
        self.print_info(f"API notifications retrieved: {len(notifications)}")

        if self.notifications_received and notifications:
            self.print_success("🎉 NOTIFICATION SYSTEM TEST PASSED!")
            self.print_info(
                "Both API and WebSocket functionality are working correctly")
            return True
        else:
            self.print_error("❌ NOTIFICATION SYSTEM TEST FAILED!")
            return False


def main():
    """Main test function"""
    print("🔔 NOTIFICATION SYSTEM COMPREHENSIVE TEST")
    print("=" * 60)

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

    # Create test users if they don't exist
    print("ℹ️  Note: This test assumes test users exist:")
    print("   - instructor@test.com / testpass123")
    print("   - student@test.com / testpass123")
    print("   If they don't exist, please create them first")

    # Run the test
    tester = NotificationTester()
    success = tester.run_comprehensive_test()

    if success:
        print("\n🎉 All tests passed! The notification system is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
