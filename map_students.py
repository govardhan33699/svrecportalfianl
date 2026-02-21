import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import CustomUser, Student
from django.conf import settings

print(f"{'User ID':<8} | {'Student ID':<10} | {'Name':<30} | {'Profile Pic Value':<40}")
print("-" * 100)

students = Student.objects.select_related('admin').all()
for s in students:
    u = s.admin
    print(f"{u.id:<8} | {s.id:<10} | {u.first_name + ' ' + u.last_name:<30} | {str(u.profile_pic):<40}")

print("\nListing all media files on disk:")
for root, dirs, files in os.walk(settings.MEDIA_ROOT):
    for f in files:
         print(f" - {f}")
