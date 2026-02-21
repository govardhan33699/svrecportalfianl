import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import CustomUser, Student

name = "GOVARDHAN REDDY BHIMAVARAPU"
print(f"Searching for '{name}'...")

users = CustomUser.objects.filter(first_name__icontains="GOVARDHAN")
print(f"Found {users.count()} users with 'GOVARDHAN' in name:")
for u in users:
    print(f"User ID: {u.id} | Email: {u.email} | Name: {u.first_name} {u.last_name} | User Type: {u.user_type}")
    try:
        print(f"  Linked Student ID: {u.student.id}")
    except:
        print("  No linked Student profile.")
    print(f"  Profile Pic: '{u.profile_pic}'")

print("\nAll students with Roll 23AM1A3124:")
students = Student.objects.filter(roll_number="23AM1A3124")
for s in students:
    u = s.admin
    print(f"Student ID: {s.id} | User ID: {u.id} | Name: {u.first_name} {u.last_name}")
