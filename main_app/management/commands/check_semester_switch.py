from django.core.management.base import BaseCommand
from django.utils import timezone
from main_app.models import Student, AcademicCalendar, Session
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Automatically switches student semesters based on the Academic Calendar'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        self.stdout.write(f"Checking semester switches for {today}...")

        # 1. Get all calendar entries where today is the commencement date
        switches = AcademicCalendar.objects.filter(commencement_date=today)

        if not switches.exists():
            self.stdout.write(self.style.SUCCESS("No semester switches scheduled for today."))
            return

        for switch in switches:
            self.stdout.write(f"Processing switch for {switch.session} - Semester {switch.semester}")
            
            # Find students in this session who need to be moved to this semester
            # Note: We assume the logical progression. 
            # If the calendar says Semester 6 starts today, any student in that session 
            # currently in Semester 5 should be moved to 6.
            
            target_semester = switch.semester
            
            # Simplified logic: Move all students in that session to the new semester
            # if they are active.
            students_updated = Student.objects.filter(
                session=switch.session
            ).update(semester=target_semester)

            self.stdout.write(self.style.SUCCESS(f"Successfully moved {students_updated} students to Semester {target_semester}"))
            
            # Logic for Admin "Saving" / Archiving:
            # Since attendance and results are now linked to the 'semester' field of those models,
            # new records created from today onwards will automatically use the new semester string
            # if the views/forms are updated to point to the student's current semester.
            # The old data remains in the DB linked to the previous semester value.

        self.stdout.write(self.style.SUCCESS("Semester automation check completed."))
