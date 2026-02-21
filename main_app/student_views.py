import json
import math
from datetime import datetime
from collections import defaultdict

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def student_home(request):
    student = get_object_or_404(Student, admin=request.user)
    total_subject = Subject.objects.filter(course=student.course).count()
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    total_present = AttendanceReport.objects.filter(student=student, status=True).count()
    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)
    subject_name = []
    data_present = []
    data_absent = []
    subjects = Subject.objects.filter(course=student.course)
    for subject in subjects:
        attendance = Attendance.objects.filter(subject=subject)
        present_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=True, student=student).count()
        absent_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=False, student=student).count()
        subject_name.append(subject.name)
        data_present.append(present_count)
        data_absent.append(absent_count)
    # Timetable for today
    from datetime import date as dt_date
    today_name = dt_date.today().strftime('%A')
    timetable_today = Timetable.objects.filter(
        course=student.course, section=student.section, day=today_name
    ).select_related('period', 'subject', 'staff').order_by('period__number')

    # Upcoming assignments
    from datetime import date as dt_date2
    upcoming_assignments = Assignment.objects.filter(
        subject__course=student.course,
        due_date__gte=dt_date2.today()
    ).order_by('due_date')[:5]

    context = {
        'total_attendance': total_attendance,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'total_subject': total_subject,
        'subjects': subjects,
        'data_present': data_present,
        'data_absent': data_absent,
        'data_name': subject_name,
        'page_title': 'Student Homepage',
        'timetable_today': timetable_today,
        'today_name': today_name,
        'upcoming_assignments': upcoming_assignments,

    }
    return render(request, 'student_template/erpnext_student_home.html', context)


@ csrf_exempt
def student_view_attendance(request):
    student = get_object_or_404(Student, admin=request.user)
    if request.method != 'POST':
        course = get_object_or_404(Course, id=student.course.id)
        context = {
            'subjects': Subject.objects.filter(course=course),
            'page_title': 'View Attendance'
        }
        return render(request, 'student_template/student_view_attendance.html', context)
    else:
        subject_id = request.POST.get('subject')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            subject = get_object_or_404(Subject, id=subject_id)
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            attendance = Attendance.objects.filter(
                date__range=(start_date, end_date), subject=subject)
            attendance_reports = AttendanceReport.objects.filter(
                attendance__in=attendance, student=student)
            json_data = []
            for report in attendance_reports:
                data = {
                    "date":  str(report.attendance.date),
                    "status": report.status
                }
                json_data.append(data)
            return JsonResponse(json.dumps(json_data), safe=False)
        except Exception as e:
            return None


def student_apply_leave(request):
    form = LeaveReportStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStudent.objects.filter(student=student),
        'page_title': 'Apply for leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('student_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_apply_leave.html", context)


def student_feedback(request):
    form = FeedbackStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStudent.objects.filter(student=student),
        'page_title': 'Student Feedback'

    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Feedback submitted for review")
                return redirect(reverse('student_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_feedback.html", context)


def student_view_profile(request):
    student = get_object_or_404(Student, admin=request.user)
    form = StudentEditForm(request.POST or None, request.FILES or None,
                           instance=student)
    context = {'form': form,
               'page_title': 'View Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = student.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    admin.profile_pic = passport
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                student.roll_number = form.cleaned_data.get('roll_number')
                student.section = form.cleaned_data.get('section')
                student.father_name = form.cleaned_data.get('father_name')
                student.mother_name = form.cleaned_data.get('mother_name')
                student.mobile_number = form.cleaned_data.get('mobile_number')
                student.parent_mobile_number = form.cleaned_data.get('parent_mobile_number')
                student.aadhar_number = form.cleaned_data.get('aadhar_number')
                student.caste = form.cleaned_data.get('caste')
                student.admission_number = form.cleaned_data.get('admission_number')
                student.academic_year = form.cleaned_data.get('academic_year')
                student.semester = form.cleaned_data.get('semester')
                student.blood_group = form.cleaned_data.get('blood_group')
                student.apaar_id = form.cleaned_data.get('apaar_id')
                student.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('student_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    return render(request, "student_template/student_view_profile.html", context)


@csrf_exempt
def student_fcmtoken(request):
    token = request.POST.get('token')
    student_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        student_user.fcm_token = token
        student_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def student_view_notification(request):
    student = get_object_or_404(Student, admin=request.user)
    notifications = NotificationStudent.objects.filter(student=student)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "student_template/student_view_notification.html", context)


def student_view_result(request):
    student = get_object_or_404(Student, admin=request.user)
    results = StudentResult.objects.filter(student=student)
    context = {
        'results': results,
        'page_title': "View Marks"
    }
    return render(request, "student_template/student_view_result.html", context)


#library

def view_books(request):
    books = Book.objects.all()
    context = {
        'books': books,
        'page_title': "Library"
    }
    return render(request, "student_template/view_books.html", context)


def student_view_timetable(request):
    student = get_object_or_404(Student, admin=request.user)
    
    # Get all periods
    periods = list(Period.objects.all().order_by('number'))
    
    # Get timetable entries
    timetable_entries = Timetable.objects.filter(
        course=student.course, section=student.section
    ).select_related('period', 'subject', 'staff', 'staff__admin')
    
    from collections import defaultdict
    DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    # Build lookup
    lookup = defaultdict(dict)
    for entry in timetable_entries:
        lookup[entry.day][entry.period.number] = entry
        
    # Build grid rows
    grid_rows = []
    for day in DAY_ORDER:
        cells = [lookup[day].get(p.number) for p in periods]
        grid_rows.append({'day': day, 'cells': cells})

    context = {
        'periods': periods,
        'grid_rows': grid_rows,
        'page_title': 'Class Timetable'
    }
    return render(request, "student_template/student_view_timetable.html", context)


def student_view_assignments(request):
    student = get_object_or_404(Student, admin=request.user)
    assignments = Assignment.objects.filter(
        subject__course=student.course
    ).order_by('-due_date')
    # Get submissions for this student
    submissions = AssignmentSubmission.objects.filter(student=student)
    submitted_ids = submissions.values_list('assignment_id', flat=True)
    context = {
        'assignments': assignments,
        'submitted_ids': list(submitted_ids),
        'page_title': 'Assignments'
    }
    return render(request, "student_template/student_view_assignments.html", context)


def student_submit_assignment(request, assignment_id):
    student = get_object_or_404(Student, admin=request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id)
    # Check if already submitted
    existing = AssignmentSubmission.objects.filter(assignment=assignment, student=student).first()
    if existing:
        messages.warning(request, "You have already submitted this assignment")
        return redirect(reverse('student_view_assignments'))
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                submission = form.save(commit=False)
                submission.assignment = assignment
                submission.student = student
                submission.save()
                messages.success(request, "Assignment Submitted Successfully")
                return redirect(reverse('student_view_assignments'))
            except Exception as e:
                messages.error(request, "Could Not Submit: " + str(e))
        else:
            messages.error(request, "Please provide a valid file")
    else:
        form = AssignmentSubmissionForm()
    context = {
        'form': form,
        'assignment': assignment,
        'page_title': f'Submit - {assignment.title}'
    }
    return render(request, "student_template/student_submit_assignment.html", context)


def student_change_password(request):
    if request.method == 'POST':
        form = StudentChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user = request.user
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password Changed Successfully! Please login again.")
            return redirect(reverse('login_page'))
        else:
            messages.error(request, "Passwords do not match")
    else:
        form = StudentChangePasswordForm()
    context = {
        'form': form,
        'page_title': 'Change Password'
    }
    return render(request, "student_template/student_change_password.html", context)


def student_attendance_report(request):
    student = get_object_or_404(Student, admin=request.user)
    subjects = Subject.objects.filter(course=student.course)
    
    # Pre-fetch Timetable to get correct faculty and period mapping for this section
    timetable = Timetable.objects.filter(
        course=student.course, 
        section=student.section
    ).select_related('staff__admin', 'period', 'subject')
    
    # Build a lookup: subject_id -> set of staff names
    subject_staff_map = {}
    # Build a lookup: {day: {subject_id: period_number}} for the grid
    tt_lookup = defaultdict(dict)
    
    for t in timetable:
        # Populate staff map
        if t.subject_id not in subject_staff_map:
            subject_staff_map[t.subject_id] = set()
        if t.staff:
            subject_staff_map[t.subject_id].add(f"{t.staff.admin.first_name} {t.staff.admin.last_name}")
            
        # Populate period lookup
        tt_lookup[t.day][t.subject_id] = t.period.number

    # 1. Subject Wise Attendance
    subject_attendance = []
    total_held = 0
    total_attended = 0
    
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject, session=student.session).count()
        present_count = AttendanceReport.objects.filter(
            attendance__subject=subject, 
            attendance__session=student.session,
            student=student, 
            status=True
        ).count()
        
        att_percent = 0
        if attendance_count > 0:
            att_percent = round((present_count / attendance_count) * 100, 2)
        
        # Determine faculty name from timetable if available, else fallback to subject default
        if subject.id in subject_staff_map and subject_staff_map[subject.id]:
            faculty_name = ", ".join(subject_staff_map[subject.id])
        else:
            faculty_name = f"{subject.staff.admin.first_name} {subject.staff.admin.last_name}"
            
        subject_attendance.append({
            'subject': subject,
            'faculty_name': faculty_name,
            'held': attendance_count,
            'attended': present_count,
            'percent': att_percent
        })
        total_held += attendance_count
        total_attended += present_count
        
    total_percent = 0
    if total_held > 0:
        total_percent = round((total_attended / total_held) * 100, 2)
        
    # 2. Date Wise Attendance Grid (Period Wise)
    periods = list(Period.objects.all().order_by('number'))
    
    # Get all attendance dates for this student's course/session
    attendance_records = AttendanceReport.objects.filter(
        student=student
    ).select_related('attendance', 'attendance__subject').order_by('-attendance__date')
    
    # Group by date
    date_map = defaultdict(lambda: defaultdict(str)) # {date: {period_number: status}}

    # Process attendance reports
    distinct_dates = []
    seen_dates = set()
    
    for report in attendance_records:
        date_obj = report.attendance.date
        date_str = date_obj.strftime("%d-%m-%Y(%a)")
        day_name = date_obj.strftime("%A")
        
        if date_str not in seen_dates:
            distinct_dates.append({'obj': date_obj, 'str': date_str, 'day': day_name})
            seen_dates.add(date_str)
            
        # Find which period this subject belongs to on this day
        subject_id = report.attendance.subject_id
        period_num = tt_lookup[day_name].get(subject_id)
        
        if period_num:
            status = "P" if report.status else "A"
            date_map[date_str][period_num] = status

    # Build the final grid
    date_wise_grid = []
    for d in distinct_dates:
        row = {'date': d['str'], 'cells': []}
        for p in periods:
            status = date_map[d['str']].get(p.number, "-")
            row['cells'].append(status)
        date_wise_grid.append(row)

    context = {
        'page_title': 'Attendance Report',
        'subject_attendance': subject_attendance,
        'total_held': total_held,
        'total_attended': total_attended,
        'total_percent': total_percent,
        'periods': periods,
        'date_wise_grid': date_wise_grid,
    }
    return render(request, "student_template/student_attendance_report.html", context)


def student_view_announcement(request):
    announcements = Announcement.objects.filter(audience__in=['all', 'student']).order_by('-created_at')
    context = {
        'announcements': announcements,
        'page_title': 'Announcements'
    }
    return render(request, "student_template/student_view_announcement.html", context)
