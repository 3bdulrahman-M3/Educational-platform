import requests
import json

# Base URL for the API
BASE_URL = 'http://localhost:8000/api/auth'

def test_register():
    """Test user registration"""
    url = f'{BASE_URL}/register/'
    data = {
        'email': 'test@example.com',
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'student',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    }
    
    response = requests.post(url, json=data)
    print(f'Register Response: {response.status_code}')
    if response.status_code == 201:
        print('Registration successful!')
        return response.json()
    else:
        print(f'Registration failed: {response.text}')
        return None

def test_login():
    """Test user login"""
    url = f'{BASE_URL}/login/'
    data = {
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    
    response = requests.post(url, json=data)
    print(f'Login Response: {response.status_code}')
    if response.status_code == 200:
        print('Login successful!')
        return response.json()
    else:
        print(f'Login failed: {response.text}')
        return None

def test_profile(access_token):
    """Test getting user profile"""
    url = f'{BASE_URL}/profile/'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(url, headers=headers)
    print(f'Profile Response: {response.status_code}')
    if response.status_code == 200:
        print('Profile retrieved successfully!')
        return response.json()
    else:
        print(f'Profile retrieval failed: {response.text}')
        return None

if __name__ == '__main__':
    print('Testing Authentication API...')
    
    # Test registration
    register_result = test_register()
    
    # Test login
    login_result = test_login()
    
    if login_result and 'tokens' in login_result:
        access_token = login_result['tokens']['access']
        
        # Test profile
        test_profile(access_token)
    
    print('API testing completed!') 