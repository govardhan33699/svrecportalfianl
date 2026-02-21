import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import Student

def dry_run():
    # Range 1: 23AM1A3167 to 23AM1A31D2 -> B
    # Range 2: 23AM1A31D3 to 24AM5A3110 -> C
    
    range1_start = '23AM1A3167'
    range1_end = '23AM1A31D2'
    range2_start = '23AM1A31D3'
    range2_end = '24AM5A3110'
    
    students = Student.objects.all().order_by('roll_number')
    
    count_b = 0
    count_c = 0
    
    print(f"{'Roll Number':<15} | {'Current Section':<15} | {'Target Section':<15}")
    print("-" * 50)
    
    for s in students:
        if not s.roll_number:
            continue
            
        target = None
        if range1_start <= s.roll_number <= range1_end:
            target = 'B'
            count_b += 1
        elif range2_start <= s.roll_number <= range2_end:
            target = 'C'
            count_c += 1
            
        if target and s.section != target:
            print(f"{s.roll_number:<15} | {s.section:<15} | {target:<15}")
            
    print("-" * 50)
    print(f"Total to update to B: {count_b}")
    print(f"Total to update to C: {count_c}")

if __name__ == "__main__":
    dry_run()
