import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import CustomUser

u = CustomUser.objects.get(student__id=22)
print(f"User {u.id} Name: {u.first_name} {u.last_name}")
print(f"Profile Pic Raw Value: {repr(u.profile_pic)}")
print(f"Profile Pic URL: {u.profile_pic.url if u.profile_pic else 'N/A'}")
