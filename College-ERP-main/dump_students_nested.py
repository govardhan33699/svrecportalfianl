import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import CustomUser, Student

with open('student_dump_nested.txt', 'w') as f:
    f.write(f"{'User ID':<8} | {'Student ID':<10} | {'Name':<30} | {'Profile Pic':<40}\n")
    f.write("-" * 100 + "\n")
    students = Student.objects.select_related('admin').all()
    for s in students:
        u = s.admin
        f.write(f"{u.id:<8} | {s.id:<10} | {u.first_name + ' ' + u.last_name:<30} | {str(u.profile_pic):<40}\n")

print("Dump created: student_dump_nested.txt")
