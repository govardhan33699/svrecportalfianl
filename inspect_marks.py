import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import Student, StudentResult, Subject

def inspect_marks():
    print("Inspecting marks for all students...")
    results = StudentResult.objects.all().select_related('student', 'subject')
    if not results.exists():
        print("No StudentResult entries found.")
        return

    for res in results:
        print(f"Student: {res.student.admin.username} ({res.student.admin.first_name})")
        print(f"  Subject: {res.subject.name}")
        print(f"  Exam Name: '{res.exam_name}'")
        print(f"  Objective: {res.objective}, Descriptive: {res.descriptive}, Assignment: {res.assignment}")
        print(f"  Total (calc): {res.total}")
        print(f"  Internal Override (internal_marks): {res.internal_marks}")
        print(f"  External Marks: {res.external_marks}")
        print("-" * 20)

if __name__ == "__main__":
    inspect_marks()
