import random
from django.core.management.base import BaseCommand
from main_app.models import CustomUser, Course, Session, Student, Staff, Subject

class Command(BaseCommand):
    help = 'Populates the database with sample data for demonstration'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # 1. Create Sessions
        session1, _ = Session.objects.get_or_create(start_year='2023-01-01', end_year='2027-12-31')
        session2, _ = Session.objects.get_or_create(start_year='2024-01-01', end_year='2028-12-31')

        # 2. Create Courses
        course_ai, _ = Course.objects.get_or_create(name='CSE - Artificial Intelligence')
        course_cs, _ = Course.objects.get_or_create(name='Computer Science & Engineering')
        course_it, _ = Course.objects.get_or_create(name='Information Technology')

        # 3. Create Staff
        staff_data = [
            ('Dr. Ramesh', 'Kumar', 'ramesh@svrec.edu.in'),
            ('Mrs. Lakshmi', 'Devi', 'lakshmi@svrec.edu.in'),
        ]
        
        for f_name, l_name, email in staff_data:
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': f_name,
                    'last_name': l_name,
                    'user_type': '2'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                Staff.objects.create(admin=user)

        # 4. Create Subjects
        subjects = [
            ('Machine Learning', course_ai, 'ramesh@svrec.edu.in'),
            ('Data Structures', course_cs, 'lakshmi@svrec.edu.in'),
            ('Python Programming', course_ai, 'ramesh@svrec.edu.in'),
            ('Database Systems', course_it, 'lakshmi@svrec.edu.in'),
        ]

        for sub_name, course, staff_email in subjects:
            staff_user = CustomUser.objects.get(email=staff_email)
            Subject.objects.get_or_create(
                name=sub_name,
                course=course,
                staff=staff_user.staff
            )

        # 5. Create Students
        student_names = [
            ('Arjun', 'Reddy', 'arjun@gmail.com', 'A', '23SV1A0501'),
            ('Sravani', 'K.', 'sravani@gmail.com', 'B', '23SV1A0502'),
            ('Vivek', 'Varma', 'vivek@gmail.com', 'A', '23SV1A0503'),
            ('Priyanka', 'M.', 'priyanka@gmail.com', 'C', '23SV1A0504'),
        ]

        for f_name, l_name, email, section, roll in student_names:
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': f_name,
                    'last_name': l_name,
                    'user_type': '3'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                Student.objects.create(
                    admin=user,
                    course=course_ai if '05' in roll else course_cs,
                    session=session1,
                    roll_number=roll,
                    section=section
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated sample data for SVREC Portal!'))
