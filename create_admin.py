import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import CustomUser, Admin

# List all admin users
print("=== Existing Admin Users ===")
admins = CustomUser.objects.filter(user_type=1)
for admin in admins:
    print(f"Email: {admin.email}")
    print(f"First Name: {admin.first_name}")
    print(f"Last Name: {admin.last_name}")
    print("---")

# Try to create a new admin with known credentials
print("\n=== Creating New Admin ===")
try:
    # Check if testadmin exists
    if CustomUser.objects.filter(email='testadmin@admin.com').exists():
        print("testadmin@admin.com already exists, updating password...")
        user = CustomUser.objects.get(email='testadmin@admin.com')
        user.set_password('admin123')
        user.save()
        print("Password updated!")
    else:
        # Create new admin user
        user = CustomUser.objects.create_user(
            email='testadmin@admin.com',
            password='admin123',
            user_type=1,
            first_name='Test',
            last_name='Admin'
        )
        # Create Admin profile
        Admin.objects.create(admin=user)
        print("New admin created!")
    
    print("\n=== NEW ADMIN CREDENTIALS ===")
    print("Email: testadmin@admin.com")
    print("Password: admin123")
    print("=============================")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
