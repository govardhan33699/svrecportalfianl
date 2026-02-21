import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import CustomUser

users = CustomUser.objects.exclude(profile_pic='')
print(f"Total users with profile_pic: {users.count()}")
for u in users:
    print(f"User {u.id}: {u.first_name} {u.last_name} | Pic: '{u.profile_pic}'")
