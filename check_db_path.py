import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from django.db import connection
print(f"Active Database Path (from settings): {connection.settings_dict['NAME']}")

from main_app.models import CustomUser
print(f"Total Users: {CustomUser.objects.all().count()}")
print(f"Total Students: {CustomUser.objects.filter(user_type=3).count()}")
