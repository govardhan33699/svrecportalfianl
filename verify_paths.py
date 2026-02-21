import os
import django
import main_app.models
import college_management_system.settings as settings_mod

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

print(f"Models File: {os.path.abspath(main_app.models.__file__)}")
print(f"Settings File: {os.path.abspath(settings_mod.__file__)}")
print(f"CWD: {os.getcwd()}")
print(f"DB Path from settings: {os.path.abspath(django.conf.settings.DATABASES['default']['NAME'])}")

from main_app.models import CustomUser
u = CustomUser.objects.filter(user_type=3).first()
if u:
    print(f"Sample Student: {u.first_name} | Pic: '{u.profile_pic}'")
else:
    print("No students found.")
