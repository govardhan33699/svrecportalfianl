import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import CustomUser

users_with_pics = []
all_users = CustomUser.objects.filter(user_type=3)
for u in all_users:
    if u.profile_pic:
        users_with_pics.append(f"User {u.id}: {u.first_name} {u.last_name} | Pic: {u.profile_pic}")

print(f"Total Students: {all_users.count()}")
print(f"Students with Pics: {len(users_with_pics)}")
for upic in users_with_pics:
    print(upic)
