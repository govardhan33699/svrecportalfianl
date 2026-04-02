import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import StudentResult

def sanitize():
    print("Starting data sanitization...")
    
    # 1. Rename MID I to Mid 1
    mid_i_count = StudentResult.objects.filter(exam_name='MID I').update(exam_name='Mid 1')
    print(f"Updated {mid_i_count} 'MID I' records to 'Mid 1'.")
    
    # 2. Rename FINAL_EXTERNAL to Final Internal
    final_ext_count = StudentResult.objects.filter(exam_name='FINAL_EXTERNAL').update(exam_name='Final Internal')
    print(f"Updated {final_ext_count} 'FINAL_EXTERNAL' records to 'Final Internal'.")
    
    print("Sanitization complete.")

if __name__ == "__main__":
    sanitize()
