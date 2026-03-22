import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()
from django.conf import settings

print(f"Resolved User: '{settings.EMAIL_HOST_USER}'")
print(f"Resolved Pass: '{settings.EMAIL_HOST_PASSWORD}'")
print(f"Pass matches hardcoded: {settings.EMAIL_HOST_PASSWORD == 'sshswdwuwaokhghd'}")
