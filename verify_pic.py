import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import CustomUser

u = CustomUser.objects.get(student__id=22)
print(f"profile_pic value: [{u.profile_pic}]")
print(f"profile_pic bool: {bool(u.profile_pic)}")
if u.profile_pic:
    print(f"Profile pic is still set! File: {u.profile_pic}")
    print("Clearing it now...")
    u.profile_pic = ''
    u.save()
    print("Cleared successfully!")
else:
    print("Profile pic is empty - placeholder should show.")
