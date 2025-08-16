#!/usr/bin/env python
"""
Simple test to verify join endpoint is working
"""

import requests
import json


def test_join_endpoint():
    """Test the join endpoint"""

    BASE_URL = "http://localhost:8000/api"
    LOGIN_URL = f"{BASE_URL}/auth/login/"
    JOIN_URL = f"{BASE_URL}/sessions/12/join/"

    print("🔍 Testing Join Endpoint Fix")
    print("=" * 50)

    # Step 1: Login to get access token
    print("🔐 Attempting login...")
    login_data = {
        "username": "testuser",  # Replace with actual test user
        "password": "testpass123"  # Replace with actual test password
    }

    try:
        login_response = requests.post(LOGIN_URL, json=login_data)
        print(f"Login Status: {login_response.status_code}")

        if login_response.status_code == 200:
            tokens = login_response.json()
            access_token = tokens.get('access')
            print("✅ Login successful")

            # Step 2: Test join endpoint
            print("\n🎯 Testing join endpoint...")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            join_data = {
                "message": "Testing join endpoint after fix"
            }

            join_response = requests.post(
                JOIN_URL, json=join_data, headers=headers)
            print(f"Join Status: {join_response.status_code}")
            print(f"Response: {join_response.text}")

            if join_response.status_code == 201:
                print("✅ Join request successful!")
                response_data = join_response.json()
                print(f"Booking Request ID: {response_data.get('id')}")
                print(f"Status: {response_data.get('status')}")

            elif join_response.status_code == 400:
                print("⚠️  Join request failed (expected for duplicate requests)")
                response_data = join_response.json()
                print(f"Error: {response_data.get('error')}")

            else:
                print(f"❌ Unexpected status code: {join_response.status_code}")

        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_join_endpoint()
    print("\n" + "=" * 50)
    print("🏁 Test completed")
