import os
import django
# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import Student

try:
    s = Student.objects.get(id=22)
    print(f"Student: {s}")
    print(f"User ID: {s.admin.id}")
    print(f"Profile Pic Field: '{s.admin.profile_pic}'")
    
    if s.admin.profile_pic:
        print(f"Url: {s.admin.profile_pic.url}")
        try:
            print(f"Path: {s.admin.profile_pic.path}")
            print(f"Exists on disk: {os.path.exists(s.admin.profile_pic.path)}")
        except Exception as e:
            print(f"Error accessing path: {e}")
            
        # Check if file exists relative to MEDIA_ROOT manually
        from django.conf import settings
        media_root = settings.MEDIA_ROOT
        manual_path = os.path.join(media_root, str(s.admin.profile_pic))
        print(f"Manual Path Check: {manual_path}")
        print(f"Exists on disk (manual): {os.path.exists(manual_path)}")
        
    else:
        print("No profile pic set in DB.")
except Exception as e:
    print(f"Error: {e}")
