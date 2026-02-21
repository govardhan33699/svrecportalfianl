import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import CustomUser

# List all admin users
print("=== Existing Admin Users ===")
admins = CustomUser.objects.filter(user_type=1)
for admin in admins:
    print(f"Email: {admin.email}, Name: {admin.first_name} {admin.last_name}")

# Update password for the first admin
if admins.exists():
    admin = admins.first()
    admin.set_password('admin123')
    admin.save()
    
    print("\n=== ADMIN CREDENTIALS (Password Reset) ===")
    print(f"Email: {admin.email}")
    print("Password: admin123")
    print("==========================================")
else:
    print("No admin users found!")
