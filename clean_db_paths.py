import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import CustomUser

users = CustomUser.objects.all()
count = 0
for u in users:
    val = str(u.profile_pic)
    if val.startswith('/media/'):
        new_val = val.replace('/media/', '', 1)
        print(f"User {u.id}: Scaling down '{val}' -> '{new_val}'")
        u.profile_pic = new_val
        u.save()
        count += 1
    elif val.startswith('media/'):
        new_val = val.replace('media/', '', 1)
        print(f"User {u.id}: Scaling down '{val}' -> '{new_val}'")
        u.profile_pic = new_val
        u.save()
        count += 1

print(f"\nCleaned {count} user profile paths.")
