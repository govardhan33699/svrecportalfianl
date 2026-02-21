import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import CustomUser, Student
from django.conf import settings

# Check ALL users with profile_pic values
users = CustomUser.objects.exclude(profile_pic='')
print(f"Users with profile_pic set: {users.count()}")
for u in users:
    pic_val = str(u.profile_pic)
    full_path = os.path.join(settings.MEDIA_ROOT, pic_val)
    exists = os.path.exists(full_path)
    print(f"  User {u.id} ({u.first_name} {u.last_name}): '{pic_val}' -> exists={exists}")
    if not exists:
        print(f"    >>> CLEARING invalid profile_pic for user {u.id}")
        u.profile_pic = ''
        u.save()
        print(f"    >>> Cleared!")

print("\nDone. All invalid profile_pic entries have been cleared.")
