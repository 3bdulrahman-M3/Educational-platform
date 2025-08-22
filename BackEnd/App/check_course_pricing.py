#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()

from courses.models import Course

def check_course_pricing():
    print("=== CHECKING COURSE PRICING ===")
    
    courses = Course.objects.all()
    print(f"Total courses: {courses.count()}")
    
    for course in courses:
        print(f"\n--- {course.title} ---")
        print(f"ID: {course.id}")
        print(f"Price: ${course.price}")
        print(f"Original Price: ${course.original_price}")
        print(f"Pricing Type: {course.pricing_type}")
        print(f"Is Free: {course.is_free}")
        print(f"Has Discount: {course.has_discount}")
        print(f"Discount %: {course.discount_percentage}")
        print(f"Display Price: {course.display_price}")
        print(f"Display Original Price: {course.display_original_price}")
        
        # Check for inconsistencies
        if course.price == 0 and course.pricing_type != 'free':
            print("❌ INCONSISTENCY: Price is 0 but pricing_type is not 'free'")
        elif course.price > 0 and course.pricing_type == 'free':
            print("❌ INCONSISTENCY: Price > 0 but pricing_type is 'free'")
        elif course.price == 0 and course.pricing_type == 'free':
            print("✅ Consistent: Free course")
        elif course.price > 0 and course.pricing_type == 'paid':
            print("✅ Consistent: Paid course")
        else:
            print("❓ Unknown pricing state")

if __name__ == "__main__":
    check_course_pricing()
