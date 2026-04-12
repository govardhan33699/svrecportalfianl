import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from main_app.models import Subject, Course, Regulation

# Complete subject data with codes
subject_data = [
    ('23A01606a', 'DM', 'Disaster Management'),
    ('23A30603b', '', 'AI for Finance'),
    ('23A30604b', 'CCAI', 'Cloud Computing for AI'),
    ('23A31601', 'BDAAA', 'Big Data Analytics & AI Applications'),
    ('23A31602P', 'FSAI LAB', 'Full Stack AI Lab'),
    ('23A31602T', 'FSAID', 'Full Stack AI Development'),
    ('23A31603b', 'BCAI', 'Blockchain for AI'),
    ('23A31605', 'BDCC LAB', 'Big Data & Cloud Computing Lab'),
    ('23A52501', '3S LAB', 'Soft skills'),
    ('23A52601', 'TPW&IPR', 'Technical Paper Writing & IPR'),
    ('CRTGHS', 'CRTGHS', 'CRT / GATE / Education Studies'),
    ('MENTORING', 'MNTG', 'MENTORING'),
]

updated_count = 0
created_count = 0
not_found = []

print("Processing subjects...\n")

for code, short_code, name in subject_data:
    try:
        # Try to find by code first
        subject = Subject.objects.get(code=code)
        old_short_code = subject.short_code
        subject.short_code = short_code if short_code else None
        subject.save()
        print(f"✓ Updated by code: {code} -> {name}")
        print(f"  Short Code: '{old_short_code}' → '{subject.short_code}'")
        updated_count += 1
    except Subject.DoesNotExist:
        # Try to find by name
        try:
            subject = Subject.objects.get(name=name)
            old_short_code = subject.short_code
            subject.short_code = short_code if short_code else None
            subject.save()
            print(f"✓ Updated by name: {name}")
            print(f"  Short Code: '{old_short_code}' → '{subject.short_code}'")
            updated_count += 1
        except Subject.DoesNotExist:
            # Subject not found - create it
            try:
                # Get default course and regulation for new subjects
                default_course = Course.objects.first()
                default_regulation = Regulation.objects.first()
                
                if default_course and default_regulation:
                    subject = Subject.objects.create(
                        code=code,
                        short_code=short_code if short_code else None,
                        name=name,
                        course=default_course,
                        regulation=default_regulation
                    )
                    print(f"✓ Created new: {code} -> {name}")
                    print(f"  Short Code: '{subject.short_code}'")
                    created_count += 1
                else:
                    print(f"✗ Cannot create {code}: Missing default Course or Regulation")
                    not_found.append((code, name))
            except Exception as e:
                print(f"✗ Error creating {code}: {str(e)}")
                not_found.append((code, name))

print(f"\n{'='*60}")
print(f"Summary:")
print(f"Updated: {updated_count}")
print(f"Created: {created_count}")
print(f"Failed: {len(not_found)}")

if not_found:
    print("\nFailed subjects:")
    for code, name in not_found:
        print(f"  - {code}: {name}")
