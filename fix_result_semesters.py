import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import StudentResult, Subject

def fix_result_semesters():
    print("Fixing StudentResult semesters...")
    results = StudentResult.objects.all().select_related('subject')
    updated_count = 0
    
    for res in results:
        target_sem = res.subject.semester
        if res.semester != target_sem:
            print(f"Updating Result ID {res.id}: {res.subject.name} - Changing sem '{res.semester}' -> '{target_sem}'")
            res.semester = target_sem
            res.save()
            updated_count += 1
            
    print(f"Update complete. {updated_count} records corrected.")

if __name__ == "__main__":
    fix_result_semesters()
