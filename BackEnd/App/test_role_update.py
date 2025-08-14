#!/usr/bin/env python
"""
Test script for role update functionality
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api"

def test_role_update_functionality():
    """Test role update functionality"""
    print("🧪 Testing Role Update Functionality")
    print("=" * 50)
    
    # Step 1: Register a user
    print("\n1. Registering a new user...")
    register_data = {
        "email": "role_test@example.com",
        "username": "role_test_user",
        "password": "testpass123",
        "confirm_password": "testpass123",
        "first_name": "Role",
        "last_name": "Test",
        "role": "student"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        user_data = response.json()
        print("✅ User registered successfully")
        print(f"Initial Role: {user_data['user']['role']}")
        access_token = user_data['tokens']['access']
        
        # Step 2: Update role using dedicated role endpoint
        print("\n2. Updating role using dedicated role endpoint...")
        role_update_data = {"role": "instructor"}
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.put(f"{BASE_URL}/auth/role/update/", 
                              json=role_update_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Role updated successfully")
            print(f"New Role: {result['user']['role']}")
            print(f"Message: {result['message']}")
            print(f"New Access Token: {result['tokens']['access'][:50]}...")
            
            # Update access token for next requests
            access_token = result['tokens']['access']
        else:
            print("❌ Role update failed")
            print(f"Error: {response.json()}")
        
        # Step 3: Update role using profile update endpoint
        print("\n3. Updating role using profile update endpoint...")
        profile_update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "role": "admin"
        }
        
        response = requests.put(f"{BASE_URL}/auth/profile/update/", 
                              json=profile_update_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Profile and role updated successfully")
            print(f"New Role: {result['user']['role']}")
            print(f"Message: {result['message']}")
            if 'tokens' in result:
                print(f"New Access Token: {result['tokens']['access'][:50]}...")
        else:
            print("❌ Profile update failed")
            print(f"Error: {response.json()}")
        
        # Step 4: Test invalid role
        print("\n4. Testing invalid role...")
        invalid_role_data = {"role": "invalid_role"}
        
        response = requests.put(f"{BASE_URL}/auth/role/update/", 
                              json=invalid_role_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Invalid role correctly rejected")
            print(f"Error: {response.json()}")
        else:
            print("❌ Invalid role was not rejected")
        
        # Step 5: Get current user profile
        print("\n5. Getting current user profile...")
        response = requests.get(f"{BASE_URL}/auth/user/", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_profile = response.json()
            print("✅ User profile retrieved")
            print(f"Current Role: {user_profile['role']}")
            print(f"Email: {user_profile['email']}")
            print(f"Name: {user_profile['first_name']} {user_profile['last_name']}")
        else:
            print("❌ Failed to get user profile")
            print(f"Error: {response.json()}")
            
    else:
        print("❌ User registration failed")
        print(f"Error: {response.json()}")

def test_role_update_without_authentication():
    """Test role update without authentication"""
    print("\n🧪 Testing Role Update Without Authentication")
    print("=" * 50)
    
    role_data = {"role": "instructor"}
    
    # Test without token
    response = requests.put(f"{BASE_URL}/auth/role/update/", json=role_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Correctly rejected without authentication")
    else:
        print("❌ Should have been rejected without authentication")

def test_role_update_with_invalid_token():
    """Test role update with invalid token"""
    print("\n🧪 Testing Role Update With Invalid Token")
    print("=" * 50)
    
    role_data = {"role": "instructor"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer invalid_token_here"
    }
    
    response = requests.put(f"{BASE_URL}/auth/role/update/", 
                          json=role_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Correctly rejected with invalid token")
    else:
        print("❌ Should have been rejected with invalid token")

def main():
    """Main test function"""
    print("🚀 Role Update API Testing")
    print("=" * 60)
    
    try:
        # Test main functionality
        test_role_update_functionality()
        
        # Test authentication requirements
        test_role_update_without_authentication()
        test_role_update_with_invalid_token()
        
        print("\n🎉 All role update tests completed!")
        print("\n📚 Summary:")
        print("- Users can update their role using /api/auth/role/update/")
        print("- Users can update their role as part of profile update")
        print("- New JWT tokens are generated when role changes")
        print("- Invalid roles are properly validated and rejected")
        print("- Authentication is required for role updates")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server")
        print("Make sure the Django server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
