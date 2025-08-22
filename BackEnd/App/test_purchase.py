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

def test_purchase_api():
    print("Testing Purchase API...")
    
    # Check if we have users and courses
    users = User.objects.all()
    courses = Course.objects.all()
    
    print(f"Found {users.count()} users")
    print(f"Found {courses.count()} courses")
    
    # Get a student user
    student = users.filter(role='student').first()
    if not student:
        print("No student users found!")
        return
    
    print(f"Using student: {student.email}")
    
    # Get a paid course
    paid_course = courses.filter(pricing_type='paid').first()
    if not paid_course:
        print("No paid courses found!")
        return
    
    print(f"Using course: {paid_course.title} (${paid_course.price})")
    
    # Test the API endpoint
    api_url = "http://localhost:8000/api/courses/"
    
    # First, try to get courses (should work without auth)
    try:
        response = requests.get(f"{api_url}?limit=5")
        print(f"GET courses status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('results', []))} courses")
    except Exception as e:
        print(f"Error getting courses: {e}")
    
    # Test purchase endpoint (should fail without auth)
    try:
        response = requests.post(f"{api_url}{paid_course.id}/purchase/")
        print(f"POST purchase status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error testing purchase: {e}")

if __name__ == "__main__":
    test_purchase_api()
