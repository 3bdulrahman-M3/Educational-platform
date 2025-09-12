#!/usr/bin/env python
"""
Simple test script to verify the chat API endpoints are working
Run this after starting the Django server
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
ADMIN_TOKEN = None  # You'll need to get this from admin login
USER_TOKEN = None   # You'll need to get this from user login

def test_chat_endpoints():
    """Test the chat API endpoints"""
    
    print("🧪 Testing Chat API Endpoints")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health/")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Get conversations (admin only)
    print("\n2. Testing conversations list (admin only)...")
    if ADMIN_TOKEN:
        headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
        try:
            response = requests.get(f"{BASE_URL}/chat/conversations/", headers=headers)
            if response.status_code == 200:
                print("✅ Conversations list accessible")
                data = response.json()
                print(f"   Found {len(data.get('results', []))} conversations")
            else:
                print(f"❌ Conversations list failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Conversations list error: {e}")
    else:
        print("⚠️  Skipping - No admin token provided")
    
    # Test 3: Get user conversation
    print("\n3. Testing user conversation...")
    if USER_TOKEN:
        headers = {"Authorization": f"Bearer {USER_TOKEN}"}
        try:
            response = requests.get(f"{BASE_URL}/chat/conversation/", headers=headers)
            if response.status_code == 200:
                print("✅ User conversation accessible")
                data = response.json()
                print(f"   Conversation ID: {data.get('id')}")
            else:
                print(f"❌ User conversation failed: {response.status_code}")
        except Exception as e:
            print(f"❌ User conversation error: {e}")
    else:
        print("⚠️  Skipping - No user token provided")
    
    # Test 4: Get unread count
    print("\n4. Testing unread count...")
    if USER_TOKEN:
        headers = {"Authorization": f"Bearer {USER_TOKEN}"}
        try:
            response = requests.get(f"{BASE_URL}/chat/unread-count/", headers=headers)
            if response.status_code == 200:
                print("✅ Unread count accessible")
                data = response.json()
                print(f"   Unread messages: {data.get('unread_count', 0)}")
            else:
                print(f"❌ Unread count failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Unread count error: {e}")
    else:
        print("⚠️  Skipping - No user token provided")
    
    print("\n" + "=" * 50)
    print("🎉 Chat API test completed!")
    print("\nTo get tokens for full testing:")
    print("1. Login as admin: POST /api/auth/login/")
    print("2. Login as user: POST /api/auth/login/")
    print("3. Update ADMIN_TOKEN and USER_TOKEN in this script")

if __name__ == "__main__":
    test_chat_endpoints()
