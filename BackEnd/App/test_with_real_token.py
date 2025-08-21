#!/usr/bin/env python
"""
Test script with real JWT token
"""
import requests
import websocket
import json
import time


def get_real_token():
    """Get a real JWT token by logging in"""
    try:
        # Try to login with a test user
        login_data = {
            "email": "youssefabdelmaged50@gmail.com",  # Use your actual email
            "password": "123456"  # Use your actual password
        }

        response = requests.post(
            'http://127.0.0.1:8000/api/auth/login/',
            json=login_data
        )

        if response.status_code == 200:
            data = response.json()
            return data.get('access')
        else:
            print(f"Login failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error getting token: {e}")
        return None


def test_with_real_token():
    """Test WebSocket with real JWT token"""
    print("🔍 Testing with Real JWT Token...")
    print("=" * 50)

    # Get real token
    token = get_real_token()
    if not token:
        print("❌ Could not get real token")
        return False

    print(f"✅ Got real token: {token[:20]}...")

    try:
        # Connect to WebSocket
        ws = websocket.create_connection(
            'ws://127.0.0.1:8000/ws/notifications/')
        print("✅ WebSocket connection established")

        # Send authentication with real token
        auth_message = {
            "type": "auth",
            "token": token
        }
        ws.send(json.dumps(auth_message))
        print("✅ Authentication message sent with real token")

        # Wait for response
        print("⏳ Waiting for authentication response...")
        response = ws.recv()
        print(f"📨 Received: {response}")

        # Parse response
        data = json.loads(response)
        if data.get('type') == 'auth_success':
            print("🎉 Authentication successful!")

            # Wait for any notifications
            print("⏳ Waiting for notifications...")
            time.sleep(3)

            # Try to receive any messages
            try:
                ws.settimeout(1)
                notification = ws.recv()
                print(f"📨 Received notification: {notification}")
            except:
                print("No notifications received (this is normal)")

        else:
            print(f"❌ Authentication failed: {data}")
            return False

        ws.close()
        print("✅ Connection closed successfully")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Real Token WebSocket Test")
    print("=" * 50)

    success = test_with_real_token()

    print("\n" + "=" * 50)
    if success:
        print("🎉 Test passed! Frontend should work with real token.")
    else:
        print("⚠️  Test failed. Check the issues above.")
