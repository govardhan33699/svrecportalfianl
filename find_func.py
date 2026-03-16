import sys
import os
sys.path.append(r'c:\Users\shiva\Downloads\SVRECPORTALMAIN')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "college_management_system.settings") # Adjust if needed

import django
django.setup()

from main_app import hod_views
import inspect

try:
    print("admin_notify_student in hod_views:", hasattr(hod_views, 'admin_notify_student'))
    if hasattr(hod_views, 'admin_notify_student'):
        func = getattr(hod_views, 'admin_notify_student')
        print("Source file:", inspect.getsourcefile(func))
        print("Source lines:", inspect.getsourcelines(func)[1])
except Exception as e:
    print("Error:", e)
