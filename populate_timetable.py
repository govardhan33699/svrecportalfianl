"""
Populate Timetable Data for B.TECH CSE-AI, VI SEM, Section A
Run with: python manage.py shell < populate_timetable.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import Period, Timetable, Subject, Staff, Course
from datetime import time

# ===== Step 1: Create 7 Periods =====
periods_data = [
    (1, time(9, 30), time(10, 20)),
    (2, time(10, 20), time(11, 10)),
    (3, time(11, 30), time(12, 20)),
    (4, time(12, 20), time(13, 10)),
    (5, time(14, 0), time(14, 50)),
    (6, time(14, 50), time(15, 40)),
    (7, time(15, 40), time(16, 30)),
]

for number, start, end in periods_data:
    period, created = Period.objects.update_or_create(
        number=number,
        defaults={'start_time': start, 'end_time': end}
    )
    status = "Created" if created else "Updated"
    print(f"  {status} Period {number}: {start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}")

print(f"\n✓ {Period.objects.count()} periods ready.\n")

# ===== Step 2: Get/Verify Course =====
# Try to find the CSE-AI course
course = None
for c in Course.objects.all():
    if 'cse' in c.name.lower() or 'ai' in c.name.lower():
        course = c
        break

if not course:
    # Use first available course or create one
    course = Course.objects.first()
    if not course:
        course = Course.objects.create(name='B.TECH CSE-AI')
        print(f"Created course: {course.name}")

print(f"Using course: {course.name} (ID: {course.id})\n")

# ===== Step 3: List existing subjects and staff =====
print("Existing subjects:")
for s in Subject.objects.filter(course=course):
    print(f"  - {s.name} (Staff: {s.staff})")

print(f"\nExisting staff:")
for s in Staff.objects.all():
    print(f"  - {s.admin.first_name} {s.admin.last_name} (ID: {s.id})")

# ===== Step 4: Subject-Faculty mapping from timetable =====
# Map short codes to full subject names and faculty short codes
SUBJECT_MAP = {
    'DM': 'Disaster Management',
    'AIF': 'AI for Finance',
    'CCAI': 'Cloud Computing for AI',
    'BDAAA': 'Big Data Analytics & AI Applications',
    'FSAI LAB': 'Full Stack AI Lab',
    'FSAID': 'Full Stack AI Development',
    'BCAI': 'Blockchain for AI',
    'BDCC LAB': 'Big Data & Cloud Computing Lab',
    'SS LAB': 'Soft Skills',
    'TPW&IPR': 'Technical Paper Writing & IPR',
    'CRTGHS': 'CRT / GATE / Education Studies',
    'MNTG': 'Mentoring',
}

# Faculty mapping: short_code -> (first_name_part, last_name_part)  for matching
FACULTY_MAP = {
    'MANJUSHA': 'MANJUSHA',
    'ALLURAIAH': 'ALLURAIAH',
    'BKB': 'KIRAN',
    'BIJJAM': 'BIJJAM',
    'AHPR': 'HARI',
    'KMM': 'MANIKYAMMA',
    'KBT': 'BINOY',
    'KARUNA': 'KARUNA',
    'YM': 'YOGESH',
}

# Subject short code -> Faculty short code
SUBJECT_FACULTY = {
    'DM': 'MANJUSHA',
    'AIF': 'ALLURAIAH',
    'CCAI': 'BKB',
    'BDAAA': 'BIJJAM',
    'FSAI LAB': 'AHPR',
    'FSAID': 'AHPR',
    'BCAI': 'KMM',
    'BDCC LAB': 'BIJJAM',
    'SS LAB': 'KBT',
    'TPW&IPR': 'KARUNA',
    'CRTGHS': 'YM',
    'MNTG': 'AHPR',
}

# ===== Step 5: Find or create subjects and map to staff =====
def find_staff(faculty_code):
    """Try to find staff member by matching name parts"""
    search_name = FACULTY_MAP.get(faculty_code, faculty_code)
    for staff in Staff.objects.all():
        full_name = f"{staff.admin.first_name} {staff.admin.last_name}".upper()
        if search_name.upper() in full_name:
            return staff
    return None

subject_objects = {}
missing_staff = []
missing_subjects = []

for short_code, full_name in SUBJECT_MAP.items():
    faculty_code = SUBJECT_FACULTY[short_code]
    staff = find_staff(faculty_code)
    
    if staff is None:
        missing_staff.append((short_code, faculty_code))
        continue
    
    # Find or create subject
    subject = Subject.objects.filter(name=full_name, course=course).first()
    if not subject:
        subject = Subject.objects.filter(name__icontains=short_code.replace(' LAB', ''), course=course).first()
    if not subject:
        subject, created = Subject.objects.get_or_create(
            name=full_name,
            course=course,
            defaults={'staff': staff}
        )
        if created:
            print(f"  Created subject: {full_name} -> Staff: {staff}")
    
    subject_objects[short_code] = (subject, staff)

if missing_staff:
    print(f"\n⚠ Missing staff members (need to create these faculty first):")
    for sc, fc in missing_staff:
        print(f"  - {sc} needs faculty: {fc} ({FACULTY_MAP.get(fc, fc)})")
    print(f"\nPlease create the missing staff members through the admin panel, then re-run this script.")

# ===== Step 6: Timetable Grid =====
# Each row: [Period1, Period2, Period3, Period4, Period5, Period6, Period7]
TIMETABLE = {
    'Monday':    ['CCAI', 'BDAAA', 'FSAID', 'DM', 'BDCC LAB', 'BDCC LAB', 'BDCC LAB'],
    'Tuesday':   ['AIF', 'BCAI', 'CRTGHS', 'CRTGHS', 'FSAI LAB', 'FSAI LAB', 'FSAI LAB'],
    'Wednesday': ['SS LAB', 'SS LAB', 'SS LAB', 'DM', 'FSAID', 'BCAI', 'TPW&IPR'],
    'Thursday':  ['BDAAA', 'CCAI', 'BCAI', 'FSAID', 'BDAAA', 'CCAI', 'AIF'],
    'Friday':    ['AIF', 'CCAI', 'BCAI', 'BDAAA', 'FSAID', 'AIF', 'MNTG'],
    'Saturday':  ['AIF', 'CCAI', 'DM', 'BDAAA', 'FSAID', 'BCAI', 'TPW&IPR'],
}

# ===== Step 7: Populate Timetable =====
created_count = 0
skipped_count = 0

for day, periods in TIMETABLE.items():
    for period_num, subject_code in enumerate(periods, start=1):
        if subject_code not in subject_objects:
            print(f"  ⚠ Skipping {day} Period {period_num}: {subject_code} (missing staff)")
            skipped_count += 1
            continue
        
        subject, staff = subject_objects[subject_code]
        period = Period.objects.get(number=period_num)
        
        entry, created = Timetable.objects.update_or_create(
            course=course,
            section='A',
            day=day,
            period=period,
            defaults={
                'subject': subject,
                'staff': staff,
            }
        )
        if created:
            created_count += 1
            
    print(f"  ✓ {day} complete")

print(f"\n{'='*50}")
print(f"✓ Created {created_count} timetable entries")
if skipped_count:
    print(f"⚠ Skipped {skipped_count} entries (missing staff)")
print(f"Total timetable entries: {Timetable.objects.filter(course=course, section='A').count()}")
