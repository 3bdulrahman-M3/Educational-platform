#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()

from authentication.models import User
from courses.models import Course

def test_login_and_purchase():
    print("Testing Login and Purchase API...")
    
    # Get a student user
    student = User.objects.filter(role='student').first()
    if not student:
        print("No student users found!")
        return
    
    print(f"Using student: {student.email}")
    
    # Get a paid course
    paid_course = Course.objects.filter(pricing_type='paid').first()
    if not paid_course:
        print("No paid courses found!")
        return
    
    print(f"Using course: {paid_course.title} (${paid_course.price})")
    
    # Test login
    login_data = {
        "email": student.email,
        "password": "testpass123"  # Try common test password
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/login/", json=login_data)
        print(f"Login status: {response.status_code}")
        print(f"Login response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            if token:
                print("Login successful! Testing purchase...")
                
                # Test purchase with token
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                purchase_response = requests.post(
                    f"http://localhost:8000/api/courses/{paid_course.id}/purchase/",
                    headers=headers
                )
                print(f"Purchase status: {purchase_response.status_code}")
                print(f"Purchase response: {purchase_response.text}")
            else:
                print("No access token in response")
        else:
            print("Login failed")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login_and_purchase()
