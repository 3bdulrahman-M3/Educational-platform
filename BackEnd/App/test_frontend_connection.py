#!/usr/bin/env python
"""
Test script to simulate frontend WebSocket connection
"""
import websocket
import json
import time


def test_frontend_connection():
    """Test WebSocket connection like the frontend does"""
    print("🔍 Testing Frontend WebSocket Connection...")
    print("=" * 50)

    # Simulate frontend connection
    try:
        # Connect to WebSocket
        ws = websocket.create_connection(
            'ws://127.0.0.1:8000/ws/notifications/')
        print("✅ WebSocket connection established")

        # Send authentication (like frontend does)
        auth_message = {
            "type": "auth",
            "token": "test_token_123"  # Simulate JWT token
        }
        ws.send(json.dumps(auth_message))
        print("✅ Authentication message sent")

        # Wait for response
        print("⏳ Waiting for authentication response...")
        response = ws.recv()
        print(f"📨 Received: {response}")

        # Send a test message
        test_message = {
            "type": "mark_read",
            "notification_id": 1
        }
        ws.send(json.dumps(test_message))
        print("✅ Test message sent")

        # Wait a bit more
        time.sleep(2)

        ws.close()
        print("✅ Connection closed successfully")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True


def test_http_endpoints():
    """Test HTTP endpoints"""
    import requests

    print("\n🔍 Testing HTTP Endpoints...")
    print("=" * 30)

    try:
        # Test courses endpoint
        response = requests.get('http://127.0.0.1:8000/api/courses/')
        print(f"✅ Courses API: {response.status_code}")

        # Test notifications endpoint
        response = requests.get('http://127.0.0.1:8000/api/notifications/')
        print(f"✅ Notifications API: {response.status_code}")

        return True
    except Exception as e:
        print(f"❌ HTTP Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Frontend Connection Test")
    print("=" * 50)

    # Test HTTP first
    http_ok = test_http_endpoints()

    # Test WebSocket
    websocket_ok = test_frontend_connection()

    print("\n" + "=" * 50)
    if http_ok and websocket_ok:
        print("🎉 All tests passed! Frontend should work.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
