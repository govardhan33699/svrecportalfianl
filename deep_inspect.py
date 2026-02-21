import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import CustomUser, Student

def dump_data(obj):
    print(f"--- Data for {obj.__class__.__name__} ---")
    for field in obj._meta.fields:
        val = getattr(obj, field.name)
        print(f"  {field.name}: {repr(val)}")

try:
    u = CustomUser.objects.get(student__id=22)
    dump_data(u)
    s = Student.objects.get(id=22)
    dump_data(s)
except Exception as e:
    print(f"Error: {e}")
