#!/usr/bin/env python
"""
Test API endpoints directly
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("🧪 Testing API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/health/")
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test chat endpoints (without auth first)
    try:
        response = requests.get(f"{BASE_URL}/api/chat/conversations/")
        print(f"📊 Conversations (no auth): {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
    except Exception as e:
        print(f"❌ Conversations test failed: {e}")
    
    # Test with authentication
    print("\n🔐 Testing with authentication...")
    
    # Login as admin
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
        if response.status_code == 200:
            token = response.json().get('access')
            print(f"✅ Login successful, token: {token[:20]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test conversations
            response = requests.get(f"{BASE_URL}/api/chat/conversations/", headers=headers)
            print(f"📊 Conversations (with auth): {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Conversations count: {len(data.get('results', data))}")
                if data.get('results') or data:
                    conv = data.get('results', data)[0] if data.get('results') else data[0]
                    print(f"   First conversation: {conv.get('user_email', 'Unknown')}")
                    
                    # Test messages
                    conv_id = conv.get('id')
                    if conv_id:
                        response = requests.get(f"{BASE_URL}/api/chat/conversations/{conv_id}/messages/", headers=headers)
                        print(f"📨 Messages: {response.status_code}")
                        if response.status_code == 200:
                            messages = response.json()
                            print(f"   Messages count: {len(messages.get('results', messages))}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
    
    print("\n🎉 API testing completed!")

if __name__ == "__main__":
    test_api()

