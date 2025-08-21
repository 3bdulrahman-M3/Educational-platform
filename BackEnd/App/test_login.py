#!/usr/bin/env python
"""
Simple login test to debug the issue
"""
import requests
import json


def test_login():
    """Test login with different approaches"""
    print("🔍 Testing Login...")
    print("=" * 30)

    # Test 1: Basic login
    print("1️⃣ Testing basic login...")
    login_data = {
        "email": "youssefabdelmaged50@gmail.com",
        "password": "Mega1411#2002"
    }

    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/auth/login/',
            json=login_data
        )

        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(
                f"Token: {data.get('tokens', {}).get('access', 'No token')[:20]}...")
        else:
            print(f"❌ Login failed")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: Check if user exists
    print("\n2️⃣ Checking if user exists...")
    try:
        response = requests.get('http://127.0.0.1:8000/api/auth/profile/')
        print(f"Profile status: {response.status_code}")
    except Exception as e:
        print(f"Profile error: {e}")


if __name__ == "__main__":
    test_login()
