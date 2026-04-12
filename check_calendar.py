import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'college_management_system.settings'
django.setup()
from main_app.models import AcademicCalendar, CalendarEvent

print("=== ALL CALENDARS ===")
for c in AcademicCalendar.objects.all().order_by('id'):
    events = CalendarEvent.objects.filter(calendar=c)
    print(f"  Cal ID={c.id}, Sem={c.get_semester_display()}, Reg={c.regulation}, "
          f"dates={c.commencement_date}/{c.instruction_end_date}, events={events.count()}")

print("\n=== ALL EVENTS ===")
for e in CalendarEvent.objects.all().order_by('calendar_id','order'):
    print(f"  Event ID={e.id}, Cal={e.calendar_id}, Type={e.event_type}, "
          f"start={e.start_date}, end={e.end_date}")
