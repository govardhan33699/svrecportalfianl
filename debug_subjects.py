import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "college_management_system.settings")
django.setup()

from main_app.models import Attendance, Student

with open("debug_output_2.txt", "w") as f:
    f.write("--- Attendance Records ---\n")
    attendance = Attendance.objects.all().order_by('-date')
    for att in attendance[:20]:
        f.write(f"Subject: {att.subject.name} | Sem: {att.semester} | Date: {att.date}\n")

    f.write("\n--- Student Semester Sample ---\n")
    st = Student.objects.first()
    f.write(f"Student: {st.admin.first_name if st else 'None'} | Sem: {st.semester if st else 'None'}\n")
