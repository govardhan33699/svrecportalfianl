import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import Student, StudentResult, Subject

def inspect_student_marks(name_substring):
    print(f"Inspecting marks for student containing '{name_substring}'...")
    students = Student.objects.filter(admin__first_name__icontains=name_substring)
    if not students.exists():
        print("No matches found.")
        return

    for student in students:
        print(f"Student: {student.admin.username} ({student.admin.first_name} {student.admin.last_name})")
        print(f"Current Semester: {student.semester}")
        results = StudentResult.objects.filter(student=student).select_related('subject')
        print(f"Found {results.count()} results.")
        for res in results:
            print(f"  Subject: {res.subject.name} (Code: {res.subject.code}, Subject Sem: {res.subject.semester})")
            print(f"    Exam Name: '{res.exam_name}'")
            print(f"    Result Sem: '{res.semester}'")
            print(f"    Internal Override (internal_marks): {res.internal_marks}")
            print(f"    Total: {res.total}")
        print("-" * 30)

if __name__ == "__main__":
    inspect_student_marks("HARISHA")
