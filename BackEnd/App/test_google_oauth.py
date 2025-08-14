#!/usr/bin/env python
"""
Test script for Google OAuth endpoints
"""
import requests
import json
import os

# API base URL
BASE_URL = "http://localhost:8000/api"


def test_google_oauth_endpoints():
    """Test Google OAuth endpoints"""
    print("🧪 Testing Google OAuth Endpoints")
    print("=" * 50)

    # Test 1: Google OAuth with invalid token
    print("\n1. Testing Google OAuth with invalid token...")
    response = requests.post(f"{BASE_URL}/auth/google/", json={
        "token": "invalid_token"
    })
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    # Test 2: Google OAuth complete with invalid data
    print("\n2. Testing Google OAuth complete with invalid data...")
    response = requests.post(f"{BASE_URL}/auth/google/complete/", json={
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "google_id": "invalid_google_id",
        "role": "student"
    })
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    # Test 3: Google OAuth complete without authentication
    print("\n3. Testing Google OAuth complete without authentication...")
    response = requests.post(f"{BASE_URL}/auth/google/complete/", json={
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "google_id": "test_google_id",
        "role": "student"
    })
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    print("\n✅ Google OAuth endpoint tests completed!")
    print("\n📝 Note: To test with real Google tokens, you need:")
    print("1. A valid Google OAuth Client ID")
    print("2. A real Google ID token from the frontend")
    print("3. Proper Google OAuth configuration")


def test_traditional_auth_with_google_id():
    """Test traditional auth and then link with Google ID"""
    print("\n🧪 Testing Traditional Auth + Google ID Linking")
    print("=" * 50)

    # Step 1: Register a user traditionally
    print("\n1. Registering user traditionally...")
    register_data = {
        "email": "test_google@example.com",
        "username": "test_google_user",
        "password": "testpass123",
        "confirm_password": "testpass123",
        "first_name": "Test",
        "last_name": "Google",
        "role": "student"
    }

    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 201:
        user_data = response.json()
        print("✅ User registered successfully")
        print(f"User ID: {user_data['user']['id']}")
        print(f"Email: {user_data['user']['email']}")
        print(f"Google ID: {user_data['user'].get('google_id', 'Not set')}")

        # Step 2: Test Google OAuth with same email (should link existing account)
        print("\n2. Testing Google OAuth with same email...")
        # This would normally use a real Google token
        # For testing, we'll just show the expected flow
        print("📝 Expected flow:")
        print("- Frontend gets Google ID token")
        print("- Backend verifies token with Google")
        print("- Backend finds existing user by email")
        print("- Backend links Google ID to existing user")
        print("- Backend returns user data with isNewUser: false")

    else:
        print("❌ User registration failed")
        print(f"Error: {response.json()}")


def test_google_oauth_flow_simulation():
    """Simulate the complete Google OAuth flow"""
    print("\n🧪 Simulating Complete Google OAuth Flow")
    print("=" * 50)

    print("\n📋 Google OAuth Flow Steps:")
    print("1. Frontend: User clicks 'Sign in with Google'")
    print("2. Frontend: Google OAuth popup/redirect")
    print("3. Frontend: Gets Google ID token")
    print("4. Frontend: Sends token to /api/auth/google/")
    print("5. Backend: Verifies token with Google")
    print("6. Backend: Checks if user exists")
    print("7. Backend: Creates user if new, or links if existing")
    print("8. Backend: Returns user data and JWT tokens")
    print("9. Frontend: If isNewUser=true, shows completion form")
    print("10. Frontend: Sends completion data to /api/auth/google/complete/")
    print("11. Backend: Updates user with role and other info")
    print("12. Backend: Returns updated user data and new tokens")

    print("\n🔧 Backend Implementation Details:")
    print("- Token verification using google-auth library")
    print("- User lookup by google_id first, then by email")
    print("- Automatic linking of existing accounts")
    print("- Role assignment during completion")
    print("- JWT token generation for authentication")
    print("- Proper error handling and validation")


def main():
    """Main test function"""
    print("🚀 Google OAuth API Testing")
    print("=" * 60)

    try:
        # Test basic endpoints
        test_google_oauth_endpoints()

        # Test traditional auth with Google linking
        test_traditional_auth_with_google_id()

        # Show complete flow
        test_google_oauth_flow_simulation()

        print("\n🎉 All tests completed!")
        print("\n📚 Next Steps:")
        print("1. Set up Google OAuth credentials in Google Cloud Console")
        print("2. Add GOOGLE_CLIENT_ID to your environment variables")
        print("3. Test with real Google tokens from your frontend")
        print("4. Implement frontend Google OAuth integration")

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server")
        print("Make sure the Django server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
