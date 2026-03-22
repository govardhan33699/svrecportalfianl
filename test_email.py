import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()
from django.core.mail import send_mail
from django.conf import settings

print(f"Backend: {settings.EMAIL_BACKEND}")
print(f"Host: {settings.EMAIL_HOST}")
print(f"User: {settings.EMAIL_HOST_USER}")

# Explicitly override DEFAULT_FROM_EMAIL for the test run
setattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)

try:
    send_mail(
        'Test Subject from College ERP',
        'This is a test to verify SMTP settings with From: header match.',
        settings.EMAIL_HOST_USER, # From_Email arg
        ['23am1a3124@svrec.ac.in'],
        fail_silently=False,
    )
    print("SUCCESS: Email sent successfully!")
except Exception as e:
    print(f"FAILURE: Failed to send email: {e}")
