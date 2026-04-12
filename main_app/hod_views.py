import json
from django.db.models import Count, Q
import requests
from datetime import date
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from .forms import *
from .models import (
    Admin, Staff, Student, Subject, Course, Session, Degree,
    Attendance, AttendanceReport, LeaveReportStudent, LeaveReportStaff,
    FeedbackStudent, FeedbackStaff, NotificationStaff, NotificationStudent,
    StudentResult, Period, Timetable, Assignment, AssignmentSubmission,
    StudyMaterial, Announcement, AcademicCalendar, CalendarEvent,
    Regulation, StudentCertificate, StudentCloudFile,
    SEMESTER_CHOICES, AcademicLevel, AcademicSemester,
    EmailTemplate, Workflow, WorkflowExecutionLog
)


def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.all().count()
    subjects = Subject.objects.annotate(attendance_count=Count('attendance'))
    total_subject = subjects.count()
    total_course = Course.objects.all().count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        subject_list.append(subject.name[:7])
        attendance_list.append(subject.attendance_count)


    # Total Subjects and students in Each Course
    
    # 1. Total Subjects and students in Each Course (Optimized)
    course_stats = Course.objects.annotate(
        subject_count=Count('subject', distinct=True),
        student_count=Count('student', distinct=True)
    )
    course_name_list = [c.name for c in course_stats]
    subject_count_list = [c.subject_count for c in course_stats]
    student_count_list_in_course = [c.student_count for c in course_stats]
    
    # Map for fast lookup
    course_student_counts = {c.id: c.student_count for c in course_stats}
    
    subject_all = subjects  # Use already fetched subjects from line 29
    subject_list = [s.name for s in subject_all]
    student_count_list_in_subject = [course_student_counts.get(s.course_id, 0) for s in subject_all]

    # 2. Student attendance stats (Optimized to avoid N+1 query loops)
    students_with_stats = Student.objects.annotate(
        present_count=Count('attendancereport', filter=Q(attendancereport__status=True), distinct=True),
        absent_count=Count('attendancereport', filter=Q(attendancereport__status=False), distinct=True),
        leave_count=Count('leavereportstudent', filter=Q(leavereportstudent__status=1), distinct=True)
    ).select_related('admin')
    
    student_attendance_present_list = [s.present_count for s in students_with_stats]
    student_attendance_leave_list = [s.leave_count + s.absent_count for s in students_with_stats]
    student_name_list = [s.admin.first_name for s in students_with_stats]


    # Today's Absentees (Optimized)
    today = date.today()
    today_absentees_reports = AttendanceReport.objects.filter(

        attendance__date=today, status=False
    ).select_related('student__admin', 'student__course', 'attendance__subject')
    
    today_absentees = []
    for report in today_absentees_reports:
        today_absentees.append({
            'student_name': report.student.admin.first_name + ' ' + report.student.admin.last_name,
            'roll_number': report.student.roll_number or 'N/A',
            'course': report.student.course.name if report.student.course else 'N/A',
            'subject': report.attendance.subject.name,
            'section': report.student.get_section_display() if hasattr(report.student, 'get_section_display') else 'N/A',
            'semester': report.student.semester if hasattr(report.student, 'semester') and report.student.semester else 'N/A',
            'period_number': report.attendance.period.number if report.attendance.period else 'N/A',
            'period_time': f"P{report.attendance.period.number} · {report.attendance.period.start_time.strftime('%I:%M')}-{report.attendance.period.end_time.strftime('%I:%M')}" if report.attendance.period else 'N/A',
        })

    absent_count = len(today_absentees)
    present_count = total_students - absent_count
    attendance_rate = round((present_count / total_students * 100), 1) if total_students > 0 else 0


    context = {
        'page_title': "Administrative Dashboard",
        'total_students': total_students,
        'total_staff': total_staff,
        'total_course': total_course,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list,
        'student_attendance_present_list': student_attendance_present_list,
        'student_attendance_leave_list': student_attendance_leave_list,
        "student_name_list": student_name_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "student_count_list_in_course": student_count_list_in_course,
        "course_name_list": course_name_list,
        "today_absentees": today_absentees,
        "absent_count": absent_count,
        "present_count": present_count,
        "attendance_rate": attendance_rate,
        "today_date": today,
        "total_degrees": Degree.objects.all().count(),
    }

    # Recent Activities
    recent_students = Student.objects.all().select_related('admin').order_by("-admin__created_at")[:3]
    recent_staff = Staff.objects.all().select_related('admin').order_by("-admin__created_at")[:3]
    recent_student_leaves = LeaveReportStudent.objects.filter(status=0).order_by("-created_at")[:3]


    activities = []
    for s in recent_students:
        activities.append({
            'type': 'student',
            'title': f"New Student: {s.admin.get_full_name()}",
            'time': s.admin.created_at,
            'icon': 'fa-user-graduate',
            'color': 'primary'
        })
    for st in recent_staff:
        activities.append({
            'type': 'staff',
            'title': f"New Staff: {st.admin.get_full_name()}",
            'time': st.admin.created_at,
            'icon': 'fa-user-tie',
            'color': 'success'
        })
    for l in recent_student_leaves:
        activities.append({
            'type': 'leave',
            'title': f"Leave Request: {l.student.admin.get_full_name()}",
            'time': l.created_at,
            'icon': 'fa-calendar-minus',
            'color': 'danger'
        })

    activities.sort(key=lambda x: x['time'], reverse=True)
    context['recent_activities'] = activities[:10]


    today = date.today()
    active_announcements = Announcement.objects.filter(Q(expires_at__isnull=True) | Q(expires_at__gte=today))

    # Grouped Announcements for Latest Updates Grid
    context['news_announcements'] = active_announcements.filter(
        category='news'
    ).order_by('-created_at')[:5]
    
    context['exam_announcements'] = active_announcements.filter(
        category__in=['mid', 'sem']
    ).order_by('-created_at')[:5]
    
    context['placement_announcements'] = active_announcements.filter(
        category__in=['event', 'holiday', 'other', 'placement']
    ).order_by('-created_at')[:5]

    return render(request, 'hod_template/home_content.html', context)


def add_staff(request):
    # ✅ FIX BUG #2: Add role validation
    if request.user.user_type != '1':
        messages.error(request, "Unauthorized access!")
        return redirect(reverse('login_page'))
    
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Staff'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type='2', first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.staff.course = course
                user.staff.father_name = form.cleaned_data.get('father_name')
                user.staff.mother_name = form.cleaned_data.get('mother_name')
                user.staff.aadhaar_number = form.cleaned_data.get('aadhaar_number')
                user.staff.pan_number = form.cleaned_data.get('pan_number')
                user.staff.spouse_name = form.cleaned_data.get('spouse_name')
                user.staff.qualification = form.cleaned_data.get('qualification')
                user.staff.blood_group = form.cleaned_data.get('blood_group')
                user.staff.designation = form.cleaned_data.get('designation')
                user.staff.faculty_role = form.cleaned_data.get('faculty_role')
                user.save()
                user.staff.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Please fulfil all requirements")

    return render(request, 'hod_template/add_staff_template.html', context)


def add_student(request):
    # ✅ FIX BUG #2: Add role validation
    if request.user.user_type != '1':
        messages.error(request, "Unauthorized access!")
        return redirect(reverse('login_page'))
    
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Add Student'}
    if request.method == 'POST':
        if student_form.is_valid():
            first_name = student_form.cleaned_data.get('first_name')
            last_name = student_form.cleaned_data.get('last_name')
            address = student_form.cleaned_data.get('address')
            email = student_form.cleaned_data.get('email')
            gender = student_form.cleaned_data.get('gender')
            password = student_form.cleaned_data.get('password')
            course = student_form.cleaned_data.get('course')
            session = student_form.cleaned_data.get('session')
            passport = request.FILES.get('profile_pic')
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type='3', first_name=first_name, last_name=last_name, profile_pic=passport)
                user.gender = gender
                user.address = address
                user.student.session = session
                user.student.course = course
                user.student.roll_number = student_form.cleaned_data.get('roll_number')
                user.student.section = student_form.cleaned_data.get('section')
                user.student.father_name = student_form.cleaned_data.get('father_name')
                user.student.mother_name = student_form.cleaned_data.get('mother_name')
                user.student.mobile_number = student_form.cleaned_data.get('mobile_number')
                user.student.parent_mobile_number = student_form.cleaned_data.get('parent_mobile_number')
                user.student.aadhar_number = student_form.cleaned_data.get('aadhar_number')
                user.student.caste = student_form.cleaned_data.get('caste')
                user.student.admission_number = student_form.cleaned_data.get('admission_number')
                user.student.academic_year = student_form.cleaned_data.get('academic_year')
                user.student.semester = student_form.cleaned_data.get('semester')
                user.student.blood_group = student_form.cleaned_data.get('blood_group')
                user.student.apaar_id = student_form.cleaned_data.get('apaar_id')
                user.student.regulation = student_form.cleaned_data.get('regulation')
                user.student.date_of_birth = student_form.cleaned_data.get('date_of_birth')
                user.student.annual_income = student_form.cleaned_data.get('annual_income')
                user.student.father_occupation = student_form.cleaned_data.get('father_occupation')
                user.student.mother_occupation = student_form.cleaned_data.get('mother_occupation')
                user.student.mother_mobile_number = student_form.cleaned_data.get('mother_mobile_number')
                user.student.nationality = student_form.cleaned_data.get('nationality')
                user.student.religion = student_form.cleaned_data.get('religion')
                user.student.mother_tongue = student_form.cleaned_data.get('mother_tongue')
                user.student.admission_date = student_form.cleaned_data.get('admission_date')
                user.student.admission_type = student_form.cleaned_data.get('admission_type')
                user.save()
                user.student.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_student'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    return render(request, 'hod_template/add_student_template.html', context)


def add_degree(request):
    form = DegreeForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                degree = Degree()
                degree.name = name
                degree.save()
                messages.success(request, "Course Added Successfully")
                return redirect(reverse('add_degree'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_degree_template.html', context)


def manage_degree(request):
    degrees = Degree.objects.all()
    context = {
        'degrees': Degree.objects.all(),
        'page_title': 'Manage Course'
    }
    return render(request, 'hod_template/manage_degree.html', context)


def ajax_delete_entity(request):
    """AJAX endpoint to delete any course-management entity."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    if request.user.user_type != '1':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    entity_type = request.POST.get('entity_type', '')
    entity_id = request.POST.get('entity_id', '')

    MODEL_MAP = {
        'subject': Subject,
        'degree': Degree,
        'year': AcademicLevel,
        'semester': AcademicSemester,
        'course': Course,
        'session': Session,
        'regulation': Regulation,
    }

    model = MODEL_MAP.get(entity_type)
    if not model:
        return JsonResponse({'success': False, 'error': f'Unknown entity type: {entity_type}'})

    try:
        obj = model.objects.get(id=entity_id)
        obj.delete()
        return JsonResponse({'success': True, 'message': f'{entity_type.title()} deleted successfully!'})
    except model.DoesNotExist:
        return JsonResponse({'success': False, 'error': f'{entity_type.title()} not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def manage_course_combined(request):
    degrees = Degree.objects.all()
    years = AcademicLevel.objects.all()
    semesters = AcademicSemester.objects.all()
    courses = Course.objects.all().select_related('degree')
    sessions = Session.objects.all()
    
    regulations = Regulation.objects.all().select_related('course', 'session').order_by('-created_at')
    calendars = AcademicCalendar.objects.all().select_related('session', 'regulation').prefetch_related('events').order_by('-session__start_year')
    timetables_count = Timetable.objects.count()

    from collections import OrderedDict
    grouped_calendars = OrderedDict()
    for cal in calendars:
        if not cal.session:
            continue
        session_key = cal.session_id
        if session_key not in grouped_calendars:
            grouped_calendars[session_key] = {
                'session': f"{cal.session.start_year.year} - {cal.session.end_year.year}",
                'calendars': []
            }
        grouped_calendars[session_key]['calendars'].append(cal)
    
    subjects = Subject.objects.all().select_related('staff__admin', 'course', 'regulation').order_by('regulation__name', 'name')
    
    context = {
        'degrees': degrees,
        'years': years,
        'semesters': semesters,
        'courses': courses,
        'sessions': sessions,
        'regulations': regulations,
        'subjects': subjects,
        'grouped_calendars': grouped_calendars,
        'timetables_count': timetables_count,
        'calendars_count': calendars.count(),
        'page_title': 'Course Management'
    }
    return render(request, 'hod_template/manage_course_combined.html', context)


def edit_degree(request, degree_id):
    instance = get_object_or_404(Degree, id=degree_id)
    form = DegreeForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'degree_id': degree_id,
        'page_title': 'Edit Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                degree = Degree.objects.get(id=degree_id)
                degree.name = name
                degree.save()
                messages.success(request, "Course Updated Successfully")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_degree_template.html', context)


def delete_degree(request, degree_id):
    degree = get_object_or_404(Degree, id=degree_id)
    try:
        degree.delete()
        messages.success(request, "Course Deleted Successfully")
    except Exception as e:
        messages.error(request, "Could Not Delete: " + str(e))
    
    referer = request.META.get('HTTP_REFERER')
    if referer and 'course_management' in referer:
        return redirect(referer)
    return redirect(reverse('manage_course_combined'))


def add_year(request):
    form = AcademicLevelForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Year'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                year = AcademicLevel()
                year.name = name
                year.save()
                messages.success(request, "Year Added Successfully")
                return redirect(reverse('add_year'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_year_template.html', context)


def manage_year(request):
    years = AcademicLevel.objects.all()
    context = {
        'years': years,
        'page_title': 'Manage Years'
    }
    return render(request, 'hod_template/manage_year.html', context)


def edit_year(request, year_id):
    instance = get_object_or_404(AcademicLevel, id=year_id)
    form = AcademicLevelForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'year_id': year_id,
        'page_title': 'Edit Year'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                year = AcademicLevel.objects.get(id=year_id)
                year.name = name
                year.save()
                messages.success(request, "Year Updated Successfully")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_year_template.html', context)


def delete_year(request, year_id):
    year = get_object_or_404(AcademicLevel, id=year_id)
    try:
        year.delete()
        messages.success(request, "Year Deleted Successfully")
    except Exception as e:
        messages.error(request, "Could Not Delete: " + str(e))
    
    referer = request.META.get('HTTP_REFERER')
    if referer and 'course_management' in referer:
        return redirect(referer)
    return redirect(reverse('manage_course_combined'))


def add_semester(request):
    form = AcademicSemesterForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Semester'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Semester Added Successfully")
                return redirect(reverse('add_semester'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_semester_template.html', context)


def manage_semester(request):
    semesters = AcademicSemester.objects.all()
    context = {
        'semesters': semesters,
        'page_title': 'Manage Semesters'
    }
    return render(request, 'hod_template/manage_semester.html', context)


def edit_semester(request, semester_id):
    instance = get_object_or_404(AcademicSemester, id=semester_id)
    form = AcademicSemesterForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'semester_id': semester_id,
        'page_title': 'Edit Semester'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Semester Updated Successfully")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_semester_template.html', context)


def delete_semester(request, semester_id):
    semester = get_object_or_404(AcademicSemester, id=semester_id)
    try:
        semester.delete()
        messages.success(request, "Semester Deleted Successfully")
    except Exception as e:
        messages.error(request, "Could Not Delete: " + str(e))
    
    referer = request.META.get('HTTP_REFERER')
    if referer and 'course_management' in referer:
        return redirect(referer)
    return redirect(reverse('manage_course_combined'))


def add_course(request):
    form = CourseForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Branch'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Branch Added Successfully")
                return redirect(reverse('add_course'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_course_template.html', context)


def edit_course(request, course_id):
    instance = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Edit Branch'
    }
    if request.method == 'POST':
        print('DEBUG POST DATA:', request.POST)
        if form.is_valid():
            try:
                course = Course.objects.get(id=course_id)
                course.name = form.cleaned_data.get('name')
                course.degree = form.cleaned_data.get('degree')
                course.save()
                messages.success(request, "Branch Updated Successfully")
                return redirect(reverse('manage_course'))
            except Exception as e:
                print('Error updating course:', str(e))
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_course_template.html', context)


def manage_course(request):
    courses = Course.objects.all().select_related('degree')
    context = {
        'courses': courses,
        'page_title': 'Manage Branches'
    }
    return render(request, 'hod_template/manage_course.html', context)


def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        course.delete()
        messages.success(request, "Branch Deleted Successfully")
    except Exception as e:
        messages.error(request, "Could Not Delete: " + str(e))
    
    referer = request.META.get('HTTP_REFERER')
    if referer and 'course_management' in referer:
        return redirect(referer)
    return redirect(reverse('manage_course_combined'))


def add_subject(request):
    form = SubjectForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_subject'))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'hod_template/add_subject_template.html', context)


def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type='2')
    context = {
        'allStaff': allStaff,
        'page_title': 'Manage Staff'
    }
    return render(request, "hod_template/manage_staff.html", context)


def manage_student(request):
    from django.db.models import Q
    enrollment_number = request.GET.get('enrollment_number')
    name = request.GET.get('name')
    semester = request.GET.get('semester')
    course_id = request.GET.get('course')
    regulation_id = request.GET.get('regulation')

    students = CustomUser.objects.filter(user_type='3').select_related(
        'student', 'student__course', 'student__semester', 'student__regulation', 'student__academic_year'
    )



    if enrollment_number:
        students = students.filter(student__roll_number__icontains=enrollment_number)
    if name:
        students = students.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))
    if semester:
        students = students.filter(student__semester=semester)
    if course_id:
        students = students.filter(student__course_id=course_id)
    if regulation_id:
        students = students.filter(student__regulation_id=regulation_id)

    courses = Course.objects.all()
    semesters = SEMESTER_CHOICES
    regulations = Regulation.objects.all()

    context = {
        'students': students,
        'courses': courses,
        'semesters': semesters,
        'regulations': regulations,
        'page_title': 'Manage Students'
    }
    return render(request, "hod_template/manage_student.html", context)


def view_student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    certificates = StudentCertificate.objects.filter(student=student).order_by('-issue_date')

    # ── CGPA Overview Calculation (Reused from student_views.py) ──
    from .models import Subject, StudentResult
    all_results = StudentResult.objects.filter(student=student).select_related('subject')
    all_subjects = Subject.objects.filter(
        course=student.course, show_in_marks=True
    ).filter(
        Q(regulation=student.regulation) | Q(regulation__isnull=True)
    ).order_by('order', 'name')

    marks_lookup = {}
    for res in all_results:
        if res.subject_id not in marks_lookup:
            marks_lookup[res.subject_id] = {}
        if res.exam_name:
            marks_lookup[res.subject_id][res.exam_name] = res.total

    grade_points_map = {'S': 10, 'A': 9, 'B': 8, 'C': 7, 'D': 6, 'E': 5, 'F': 0}
    total_credits = 0.0
    total_earned_credits = 0.0
    total_grade_points = 0.0
    total_marks_sum = 0.0
    total_sub_count = 0
    total_backlogs = 0
    semesters_with_data = 0

    for sem_key in ['1', '2', '3', '4', '5', '6', '7', '8']:
        sem_cr = 0.0
        sem_gp = 0.0
        sem_has_data = False
        sem_subs = [sub for sub in all_subjects if (sub.semester or '1') == sem_key]
        for sub in sem_subs:
            res = all_results.filter(subject=sub).filter(Q(semester=sem_key) | Q(semester__isnull=True)).first()
            if not res:
                res = all_results.filter(subject=sub).first()

            if res and res.internal_marks:
                im = res.internal_marks
            else:
                sub_marks = marks_lookup.get(sub.id, {})
                int1 = float(sub_marks.get('Mid 1', sub_marks.get('INT-1', sub_marks.get('MID-1', 0))) or 0)
                int2 = float(sub_marks.get('Mid 2', sub_marks.get('INT-2', sub_marks.get('MID-2', 0))) or 0)
                m_max = max(int1, int2)
                m_min = min(int1, int2)
                im = round((0.8 * m_max) + (0.2 * m_min))

            em = res.external_marks if res else ''
            tot = im + (float(em) if em else 0)

            if em == '' and im == 0:
                continue

            sem_has_data = True
            status = 'P' if tot >= 40 else 'F'
            if tot >= 90: grade = 'S'
            elif tot >= 80: grade = 'A'
            elif tot >= 70: grade = 'B'
            elif tot >= 60: grade = 'C'
            elif tot >= 50: grade = 'D'
            elif tot >= 40: grade = 'E'
            else: grade = 'F'

            cr_val = float(sub.credits or 0)
            gp_weight = grade_points_map.get(grade, 0)
            sem_cr += cr_val
            sem_gp += gp_weight * cr_val
            total_marks_sum += tot
            total_sub_count += 1
            if status == 'F':
                total_backlogs += 1
            else:
                total_earned_credits += cr_val

        if sem_has_data:
            semesters_with_data += 1
            total_credits += sem_cr
            total_grade_points += sem_gp

    cgpa = round(total_grade_points / total_credits, 2) if total_credits > 0 else 0.0
    overall_percentage = round((cgpa - 0.75) * 10, 2) if cgpa > 0 else 0.0
    max_cgpa = 10.0

    if overall_percentage >= 70:
        class_awarded = 'First Class with Distinction'
    elif overall_percentage >= 60:
        class_awarded = 'First Class'
    elif overall_percentage >= 50:
        class_awarded = 'Second Class'
    elif overall_percentage >= 40:
        class_awarded = 'Pass'
    else:
        class_awarded = 'N/A'

    context = {
        'student': student,
        'certificates': certificates,
        'page_title': 'View Student Details',
        # CGPA Overview
        'cgpa': cgpa,
        'overall_percentage': overall_percentage,
        'total_backlogs': total_backlogs,
        'class_awarded': class_awarded,
        'total_semesters_with_data': semesters_with_data,
        'total_credits': total_credits,
        'total_earned_credits': total_earned_credits,
        'max_cgpa': max_cgpa,
    }
    return render(request, "hod_template/view_student_detail.html", context)


def add_student_certificate(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentCertificateForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.student = student
            certificate.save()
            messages.success(request, "Certificate added successfully")
            return redirect(reverse('view_student_detail', args=[student_id]))
        else:
            messages.error(request, "Failed to add certificate. Please check the form.")
    
    context = {
        'form': form,
        'student': student,
        'page_title': 'Add Student Certificate'
    }
    return render(request, "hod_template/final_certificate_form.html", context)


def edit_student_certificate(request, student_id, certificate_id):
    student = get_object_or_404(Student, id=student_id)
    certificate = get_object_or_404(StudentCertificate, id=certificate_id)
    form = StudentCertificateForm(request.POST or None, request.FILES or None, instance=certificate)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Certificate updated successfully")
            return redirect(reverse('view_student_detail', args=[student_id]))
        else:
            messages.error(request, "Failed to update certificate. Please check the form.")
            
    context = {
        'form': form,
        'student': student,
        'certificate': certificate,
        'page_title': 'Edit Student Certificate'
    }
    return render(request, "hod_template/final_certificate_form.html", context)


def delete_student_certificate(request, student_id, certificate_id):
    certificate = get_object_or_404(StudentCertificate, id=certificate_id)
    certificate.delete()
    messages.success(request, "Certificate deleted successfully")
    return redirect(reverse('view_student_detail', args=[student_id]))


def manage_email_templates(request):
    templates = EmailTemplate.objects.all()
    context = {
        'templates': templates,
        'page_title': 'Manage Email Templates'
    }
    return render(request, "hod_template/manage_email_templates.html", context)


def add_email_template(request):
    form = EmailTemplateForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Email template added successfully")
            return redirect(reverse('manage_email_templates'))
        else:
            messages.error(request, "Failed to add email template")
    context = {
        'form': form,
        'page_title': 'Add Email Template'
    }
    return render(request, "hod_template/add_email_template_template.html", context)


def edit_email_template(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id)
    form = EmailTemplateForm(request.POST or None, instance=template)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Email template updated successfully")
            return redirect(reverse('manage_email_templates'))
        else:
            messages.error(request, "Failed to update email template")
    context = {
        'form': form,
        'template_id': template_id,
        'page_title': 'Edit Email Template'
    }
    return render(request, "hod_template/add_email_template_template.html", context)


def delete_email_template(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id)
    template.delete()
    messages.success(request, "Email template deleted successfully")
    return redirect(reverse('manage_email_templates'))


def manage_workflows(request):
    workflows = Workflow.objects.all()
    context = {
        'workflows': workflows,
        'page_title': 'Manage Workflows'
    }
    return render(request, "hod_template/manage_workflows.html", context)


def workflow_builder(request, workflow_id=None):
    workflow = None
    if workflow_id:
        workflow = get_object_or_404(Workflow, id=workflow_id)
    
    email_templates = EmailTemplate.objects.all()
    semesters = [{'id': c[0], 'name': c[1]} for c in SEMESTER_CHOICES]
    courses = Course.objects.all()

    # Serialize for json_script
    email_templates_json = [{'id': t.id, 'name': t.name} for t in email_templates]
    courses_json = [{'id': c.id, 'name': c.name} for c in courses]
    semesters_json = semesters
    
    context = {
        'workflow': workflow,
        'email_templates': email_templates,
        'email_templates_json': email_templates_json,
        'courses': courses,
        'courses_json': courses_json,
        'semesters': semesters,
        'semesters_json': semesters_json,
        'page_title': 'Workflow Builder'
    }
    return render(request, "hod_template/workflow_builder.html", context)


def save_workflow(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            workflow_id = data.get('id')
            name = data.get('name')
            trigger_type = data.get('trigger_type')
            graph_data = data.get('graph_data')
            
            if workflow_id:
                workflow = Workflow.objects.get(id=workflow_id)
                workflow.name = name
                workflow.trigger_type = trigger_type
                workflow.graph_data = graph_data
                workflow.save()
            else:
                Workflow.objects.create(
                    name=name,
                    trigger_type=trigger_type,
                    graph_data=graph_data
                )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def delete_workflow(request, workflow_id):
    workflow = get_object_or_404(Workflow, id=workflow_id)
    workflow.delete()
    messages.success(request, "Workflow deleted successfully")
    return redirect(reverse('manage_workflows'))



def manage_subject(request):
    from collections import OrderedDict
    SEMESTER_DISPLAY = {
        '1': 'I B.Tech. I Sem.',
        '2': 'I B.Tech. II Sem.',
        '3': 'II B.Tech. I Sem.',
        '4': 'II B.Tech. II Sem.',
        '5': 'III B.Tech. I Sem.',
        '6': 'III B.Tech. II Sem.',
        '7': 'IV B.Tech. I Sem.',
        '8': 'IV B.Tech. II Sem.',
    }
    subjects = Subject.objects.all().select_related('staff__admin', 'course', 'regulation').order_by('semester', 'name')
    
    semester_subjects = OrderedDict()
    for sem_key in ['1', '2', '3', '4', '5', '6', '7', '8']:
        sem_name = SEMESTER_DISPLAY[sem_key]
        sem_subs = [s for s in subjects if s.semester == sem_key]
        semester_subjects[sem_name] = sem_subs
    
    # Unassigned subjects (no semester)
    unassigned = [s for s in subjects if not s.semester]
    if unassigned:
        semester_subjects['Unassigned'] = unassigned

    context = {
        'semester_subjects': semester_subjects,
        'page_title': 'Manage Subjects'
    }
    return render(request, "hod_template/manage_subject.html", context)


def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    form = StaffForm(request.POST or None, instance=staff)
    formset = StaffQualificationFormSet(request.POST or None, instance=staff)
    context = {
        'form': form,
        'formset': formset,
        'staff_id': staff_id,
        'page_title': 'Edit Staff'
    }
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=staff.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    user.profile_pic = passport
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                staff.course = course
                staff.father_name = form.cleaned_data.get('father_name')
                staff.mother_name = form.cleaned_data.get('mother_name')
                staff.aadhaar_number = form.cleaned_data.get('aadhaar_number')
                staff.pan_number = form.cleaned_data.get('pan_number')
                staff.spouse_name = form.cleaned_data.get('spouse_name')
                staff.qualification = form.cleaned_data.get('qualification')
                staff.blood_group = form.cleaned_data.get('blood_group')
                staff.designation = form.cleaned_data.get('designation')
                staff.faculty_role = form.cleaned_data.get('faculty_role')
                staff.date_of_birth = form.cleaned_data.get('date_of_birth')
                staff.date_of_joining = form.cleaned_data.get('date_of_joining')
                staff.experience = form.cleaned_data.get('experience')
                staff.mobile_number = form.cleaned_data.get('mobile_number')
                user.save()
                staff.save()
                formset.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fill form properly")
    
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentEditForm(request.POST or None, instance=student)
    context = {
        'form': form,
        'student_id': student_id,
        'page_title': 'Edit Student'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            session = form.cleaned_data.get('session')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=student.admin.id)
                if passport != None:
                    user.profile_pic = passport
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                student.session = session
                user.gender = gender
                user.address = address
                student.course = course
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
                student.regulation = form.cleaned_data.get('regulation')
                student.date_of_birth = form.cleaned_data.get('date_of_birth')
                student.annual_income = form.cleaned_data.get('annual_income')
                student.father_occupation = form.cleaned_data.get('father_occupation')
                student.mother_occupation = form.cleaned_data.get('mother_occupation')
                student.mother_mobile_number = form.cleaned_data.get('mother_mobile_number')
                student.nationality = form.cleaned_data.get('nationality')
                student.religion = form.cleaned_data.get('religion')
                student.mother_tongue = form.cleaned_data.get('mother_tongue')
                student.admission_date = form.cleaned_data.get('admission_date')
                student.admission_type = form.cleaned_data.get('admission_type')
                user.save()
                student.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_student', args=[student_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    
    return render(request, "hod_template/edit_student_template.html", context)


def edit_course(request, course_id):
    instance = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Edit Branch'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course.objects.get(id=course_id)
                course.name = name
                course.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_course_template.html', context)


def edit_subject(request, subject_id):
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Edit Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_subject', args=[subject_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    return render(request, 'hod_template/edit_subject_template.html', context)


def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Academic Year'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Academic Year Created")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_session_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Manage Academic Years'}
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Edit Academic Year'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Academic Year Updated")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Academic Year Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


def student_feedback_message(request):
    # ✅ FIX BUG #3: Add role validation
    if request.user.user_type != '1':
        if request.method == 'POST':
            return HttpResponse(False)
        return redirect(reverse('login_page'))
    
    if request.method != 'POST':
        feedbacks = FeedbackStudent.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Student Feedback Messages'
        }
        return render(request, 'hod_template/student_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStudent, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


def staff_feedback_message(request):
    # ✅ FIX BUG #3: Add role validation
    if request.user.user_type != '1':
        if request.method == 'POST':
            return HttpResponse(False)
        return redirect(reverse('login_page'))
    
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Staff Feedback Messages'
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


def view_staff_leave(request):
    # ✅ FIX BUG #3: Add role validation to CSRF-exempt endpoint
    if request.user.user_type != '1':
        if request.method == 'POST':
            return HttpResponse(False)
        return redirect(reverse('login_page'))
    
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Staff'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def view_student_leave(request):
    # ✅ FIX BUG #3: Add role validation to CSRF-exempt endpoint
    if request.user.user_type != '1':
        if request.method == 'POST':
            return HttpResponse(False)
        return redirect(reverse('login_page'))
    
    if request.method != 'POST':
        allLeave = LeaveReportStudent.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Students'
        }
        return render(request, "hod_template/student_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStudent, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    courses = Course.objects.all()
    sessions = Session.objects.all()
    sections = Student.SECTION
    semesters = SEMESTER_CHOICES
    regulations = Regulation.objects.all()

    students_data = []
    subjects_list = []
    summary = {'below_60': 0, 'between_60_65': 0, 'avg': 0, 'above_75': 0}
    total_students = 0
    filters_applied = False

    course_id = request.GET.get('course')
    section = request.GET.get('section')
    semester = request.GET.get('semester')
    session_id = request.GET.get('session')
    regulation_id = request.GET.get('regulation')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if course_id and session_id:
        filters_applied = True
        # Get subjects for this course filtered by semester
        subjects_qs = Subject.objects.filter(course_id=course_id)
        if semester:
            subjects_qs = subjects_qs.filter(semester=semester)
        subjects_list = list(subjects_qs)

        # Get students matching filters
        student_qs = Student.objects.filter(course_id=course_id).select_related('admin', 'course', 'regulation')
        if section:
            student_qs = student_qs.filter(section=section)
        if semester:
            student_qs = student_qs.filter(semester=semester)
        if regulation_id:
            student_qs = student_qs.filter(regulation_id=regulation_id)

        # Build attendance filter
        att_filter = {'session_id': session_id}
        if semester:
            att_filter['semester'] = semester
        if from_date:
            att_filter['date__gte'] = from_date
        if to_date:
            att_filter['date__lte'] = to_date

        for student in student_qs:
            row = {
                'roll_number': student.roll_number or 'N/A',
                'name': f"{student.admin.first_name} {student.admin.last_name}",
                'subjects': [],
                'total_classes': 0,
                'total_attended': 0,
                'percentage': 0,
            }
            for subject in subjects_list:
                # Total attendance records for this subject within filters
                total = AttendanceReport.objects.filter(
                    student=student,
                    attendance__subject=subject,
                    **{f'attendance__{k}': v for k, v in att_filter.items()}
                ).count()
                present = AttendanceReport.objects.filter(
                    student=student,
                    attendance__subject=subject,
                    status=True,
                    **{f'attendance__{k}': v for k, v in att_filter.items()}
                ).count()
                row['subjects'].append({'total': total, 'present': present})
                row['total_classes'] += total
                row['total_attended'] += present

            if row['total_classes'] > 0:
                row['percentage'] = round((row['total_attended'] / row['total_classes']) * 100, 2)
                if float(row['percentage']).is_integer():
                    row['percentage'] = int(row['percentage'])

            row['excused_absent'] = row['total_classes'] - row['total_attended']

            # Summary calculation
            pct = row['percentage']
            if pct < 60:
                summary['below_60'] += 1
            elif pct < 65:
                summary['between_60_65'] += 1
            elif pct < 75:
                summary['avg'] += 1
            else:
                summary['above_75'] += 1

            students_data.append(row)
            total_students += 1

        # Compute max classes per subject (total attendance records for each subject)
        for subject in subjects_list:
            max_cls = Attendance.objects.filter(
                subject=subject,
                **att_filter
            ).count()
            subject.max_classes = max_cls

    # Get descriptive names for selected filters for printing
    selected_course = Course.objects.filter(id=course_id).first() if course_id else None
    selected_session = Session.objects.filter(id=session_id).first() if session_id else None
    selected_semester_name = next((n for v, n in semesters if v == semester), '') if semester else 'All'

    # Get degree name from course
    degree_name = ''
    if selected_course and selected_course.degree:
        degree_name = selected_course.degree.name

    from datetime import date
    context = {
        'courses': courses,
        'sessions': sessions,
        'sections': sections,
        'semesters': semesters,
        'regulations': regulations,
        'subjects': subjects_list,
        'students_data': students_data,
        'summary': summary,
        'total_students': total_students,
        'filters_applied': filters_applied,
        'page_title': 'View Attendance',
        'selected_course': selected_course,
        'selected_session': selected_session,
        'selected_semester_name': selected_semester_name,
        'selected_section': section if section else 'All',
        'from_date': from_date or '',
        'to_date': to_date or '',
        'report_date': date.today().strftime('%d/%m/%Y'),
        'degree_name': degree_name,
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


def admin_view_marks_report(request):
    courses = Course.objects.all()
    sessions = Session.objects.all()
    sections = Student.SECTION
    semesters = SEMESTER_CHOICES
    regulations = Regulation.objects.all()

    students_data = []
    subjects_list = []
    filters_applied = False

    course_id = request.GET.get('course')
    section = request.GET.get('section')
    semester = request.GET.get('semester')
    session_id = request.GET.get('session')
    regulation_id = request.GET.get('regulation')
    exam_name = request.GET.get('exam_name')

    if course_id and session_id:
        filters_applied = True
        subjects_qs = Subject.objects.filter(course_id=course_id)
        if semester:
            subjects_qs = subjects_qs.filter(semester=semester)
        if regulation_id:
            subjects_qs = subjects_qs.filter(regulation_id=regulation_id)
        subjects_list = list(subjects_qs)

        student_qs = Student.objects.filter(course_id=course_id).select_related('admin', 'course', 'regulation')
        if section:
            student_qs = student_qs.filter(section=section)
        if semester:
            student_qs = student_qs.filter(semester=semester)
        if regulation_id:
            student_qs = student_qs.filter(regulation_id=regulation_id)

        for student in student_qs:
            row = {
                'roll_number': student.roll_number or 'N/A',
                'name': f"{student.admin.first_name} {student.admin.last_name}",
                'marks_list': [],
                'total_marks': 0,
            }
            for subject in subjects_list:
                result = StudentResult.objects.filter(
                    student=student,
                    subject=subject,
                    exam_name=exam_name
                ).first()
                mark = result.total if result else 0
                if float(mark).is_integer():
                    mark = int(mark)
                row['marks_list'].append(mark)
                if result:
                    row['total_marks'] += result.total

            if float(row['total_marks']).is_integer():
                row['total_marks'] = int(row['total_marks'])
            students_data.append(row)

    # Get unique exam names for the filter dropdown
    exam_names = StudentResult.objects.values_list('exam_name', flat=True).distinct()
    exam_names = [e for e in exam_names if e]  # filter out None

    # Get descriptive names for selected filters for printing
    selected_course = Course.objects.filter(id=course_id).first() if course_id else None
    selected_session = Session.objects.filter(id=session_id).first() if session_id else None
    selected_semester_name = next((n for v, n in semesters if v == semester), '') if semester else 'All'

    context = {
        'courses': courses,
        'sessions': sessions,
        'sections': sections,
        'semesters': semesters,
        'regulations': regulations,
        'exam_names': exam_names,
        'subjects': subjects_list,
        'students_data': students_data,
        'filters_applied': filters_applied,
        'page_title': 'View Marks Report',
        'selected_course': selected_course,
        'selected_session': selected_session,
        'selected_semester_name': selected_semester_name,
        'selected_section': section if section else 'All'
    }

    return render(request, "hod_template/admin_view_marks_report.html", context)


def get_admin_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, session=session)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.student)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    custom_user.profile_pic = passport
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.email = form.cleaned_data.get('email')
                custom_user.gender = form.cleaned_data.get('gender')
                custom_user.address = form.cleaned_data.get('address')
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def admin_notify_staff(request):
    staff = CustomUser.objects.filter(user_type='2')
    context = {
        'page_title': "Send Notifications To Staff",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)


def admin_notify_student(request):
    student = CustomUser.objects.filter(user_type='3')
    context = {
        'page_title': "Send Notifications To Students",
        'students': student
    }
    return render(request, "hod_template/student_notification.html", context)


def send_student_notification(request):
    # ✅ FIX BUG #3: Add role validation
    if request.user.user_type != '1':
        return HttpResponse("False")
    
    id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(Student, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('student_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': student.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStudent(student=student, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def send_staff_notification(request):
    # ✅ FIX BUG #3: Add role validation
    if request.user.user_type != '1':
        return HttpResponse("False")
    
    id = request.POST.get('id')
    message = request.POST.get('message')
    staff = get_object_or_404(Staff, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('staff_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': staff.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStaff(staff=staff, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_staff(request, staff_id):
    # ✅ FIX BUG #2: Add role validation
    if request.user.user_type != '1':
        messages.error(request, "Unauthorized access!")
        return redirect(reverse('login_page'))
    
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse('manage_staff'))


def delete_student(request, student_id):
    # ✅ FIX BUG #2: Add role validation
    if request.user.user_type != '1':
        messages.error(request, "Unauthorized access!")
        return redirect(reverse('login_page'))
    
    student = get_object_or_404(Student, id=student_id)
    try:
        # Manually delete related records that might cause FK issues
        AttendanceReport.objects.filter(student=student).delete()
        LeaveReportStudent.objects.filter(student=student).delete()
        FeedbackStudent.objects.filter(student=student).delete()
        NotificationStudent.objects.filter(student=student).delete()
        StudentResult.objects.filter(student=student).delete()
        
        # Finally delete the user which will cascade delete the student profile
        user = student.admin
        user.delete()
        messages.success(request, "Student deleted successfully!")
    except Exception as e:
        messages.error(request, "Error occurred while deleting student: " + str(e))
    return redirect(reverse('manage_student'))


# Removed duplicate delete_course (already defined above)


def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject deleted successfully!")
    except Exception as e:
        messages.error(request, "Could Not Delete: " + str(e))
        
    referer = request.META.get('HTTP_REFERER')
    if referer and 'course_management' in referer:
        return redirect(referer)
    return redirect(reverse('manage_course_combined'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Academic Year deleted successfully!")
    except Exception as e:
        messages.error(
            request, "Error occurred: " + str(e))
            
    referer = request.META.get('HTTP_REFERER')
    if referer and 'course_management' in referer:
        return redirect(referer)
    return redirect(reverse('manage_course_combined'))

def import_student(request):
    if request.method == 'POST':
        import pandas as pd
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            messages.error(request, "Please upload an Excel file")
            return redirect(reverse('import_student'))
        
        try:
            df = pd.read_excel(excel_file)
            
            # Normalize column names (strip space and lowercase)
            df.columns = [str(col).strip().lower() for col in df.columns]
            
            # Helper to get value from various possible column names
            def get_val(row, aliases):
                for alias in aliases:
                    if alias.lower() in df.columns:
                        return str(row[alias.lower()]).strip()
                return None

            success_count = 0
            errors = []
            
            for index, row in df.iterrows():
                row_num = index + 2  # 1-based + 1 for header
                try:
                    email = get_val(row, ['Email', 'Email Address'])
                    
                    # Silently skip rows that are completely empty or missing core data
                    if not email or email == 'nan' or email.strip() == '':
                        continue
                        
                    if CustomUser.objects.filter(email=email).exists():
                        errors.append(f"Row {row_num}: Email {email} already exists")
                        continue
                    
                    first_name = get_val(row, ['First Name', 'FirstName'])
                    if not first_name or first_name == 'nan':
                        continue # Skip empty rows
                    
                    password = get_val(row, ['Password']) or 'student123'
                    last_name = get_val(row, ['Last Name', 'LastName']) or ""
                    gender_raw = get_val(row, ['Gender']) or 'Male'
                    gender = 'M' if gender_raw.lower().startswith('m') else 'F'
                    address = get_val(row, ['Address']) or 'NANDYAL'
                    roll_number = get_val(row, ['Roll Number', 'RollNo', 'Roll'])
                    course_name = get_val(row, ['Branch', 'Course', 'Department'])
                    session_year = get_val(row, ['Academic Year', 'Session Start Year', 'Year', 'Session'])
                    
                    if not course_name or course_name == 'nan':
                        errors.append(f"Row {row_num}: Missing Branch Name")
                        continue
                    
                    course = Course.objects.filter(name__icontains=course_name.strip()).first()
                    if not course:
                        available_courses = list(Course.objects.all().values_list('name', flat=True))
                        errors.append(f"Row {row_num}: Branch '{course_name}' not found. Available: {available_courses}")
                        continue
                        
                    # Try to find session by year
                    session = None
                    if session_year and session_year != 'nan':
                        # Convert session_year to int if possible
                        try:
                            year_int = int(float(session_year))
                            session = Session.objects.filter(start_year__year=year_int).first()
                        except:
                            pass
                    
                    if not session:
                        session = Session.objects.first()
                        if not session:
                            errors.append(f"Row {row_num}: No Academic Years exist.")
                            continue
                    
                    user = CustomUser.objects.create_user(
                        email=email, 
                        password=password, 
                        user_type='3', 
                        first_name=first_name, 
                        last_name=last_name
                    )
                    user.gender = gender
                    user.address = address
                    user.save()
                    
                    # Profile created via signal, now update Student fields
                    student = user.student
                    student.course = course
                    student.session = session
                    student.roll_number = roll_number if (roll_number and roll_number != 'nan') else f"STU{user.id}"
                    student.save()
                    
                    success_count += 1
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            if success_count > 0:
                messages.success(request, f"Successfully imported {success_count} students.")
            
            if errors:
                # Show first 10 errors to avoid flooding
                err_msg = "Import Errors: " + " | ".join(errors[:10])
                if len(errors) > 10:
                    err_msg += f" ... and {len(errors)-10} more"
                messages.error(request, err_msg)
                
            return redirect(reverse('manage_student'))
            
        except Exception as e:
            messages.error(request, "Error processing file: " + str(e))
            return redirect(reverse('import_student'))
            
    courses = Course.objects.all()
    sessions = Session.objects.all()
    return render(request, "hod_template/import_student_template.html", {
        'page_title': 'Import Students',
        'courses': courses,
        'sessions': sessions
    })


def manage_timetable(request):
    from collections import defaultdict
    periods = list(Period.objects.all().order_by('number'))
    courses = Course.objects.all()
    
    selected_course_id = request.GET.get('course')
    selected_semester = request.GET.get('semester')
    
    # Default to first course if not selected
    if not selected_course_id:
        first_course = courses.first()
        if first_course:
            selected_course_id = first_course.id
            
    try:
        selected_course_id = int(selected_course_id) if selected_course_id else None
    except:
        selected_course_id = None

    staff_timetable_list = []
    if selected_course_id:
        # Filter timetables by course AND semester if provided
        timetable_filter = {'course_id': selected_course_id}
        if selected_semester:
            timetable_filter['semester'] = selected_semester
            
        course_timetables = Timetable.objects.filter(**timetable_filter).select_related('staff__admin')
        
        # Get unique staff members who have a timetable entry in this course/semester
        teaching_staff_ids = list(course_timetables.values_list('staff_id', flat=True).distinct())
        
        # Also get staff who "belong" to this course (we show them even if empty)
        belonging_staff_ids = list(Staff.objects.filter(course_id=selected_course_id).values_list('id', flat=True))
        
        # Combined set of staff to show
        all_staff_ids = set(teaching_staff_ids + belonging_staff_ids)
        
        staff_list = Staff.objects.filter(id__in=all_staff_ids).select_related('admin')
        
        # Group timetables by staff
        all_timetables = Timetable.objects.filter(**timetable_filter, staff__in=staff_list).select_related('period', 'subject', 'course')
        
        staff_map = defaultdict(list)
        for t in all_timetables:
            staff_map[t.staff_id].append(t)
            
        DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        for staff in staff_list:
            lookup = defaultdict(dict)
            for t in staff_map[staff.id]:
                lookup[t.day][t.period.number] = t
            
            grid_rows = []
            for day in DAY_ORDER:
                cells = []
                for p in periods:
                    cells.append(lookup[day].get(p.number))
                grid_rows.append({'day': day, 'cells': cells})
            
            staff_timetable_list.append({'staff': staff, 'grid_rows': grid_rows})

    for c in courses:
        c.selected = (c.id == selected_course_id)

    context = {
        'periods': periods,
        'courses': courses,
        'selected_course_id': selected_course_id,
        'selected_semester': selected_semester,
        'semester_choices': SEMESTER_CHOICES,
        'staff_timetable_list': staff_timetable_list,
        'page_title': 'Manage Timetables'
    }
    return render(request, "hod_template/manage_timetable.html", context)


def add_timetable(request):
    form = TimetableForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Timetable Entry'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Timetable Entry Added Successfully")
                return redirect(reverse('add_timetable'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Please fill the form properly")
    return render(request, 'hod_template/add_timetable_template.html', context)


def edit_timetable(request, timetable_id):
    instance = get_object_or_404(Timetable, id=timetable_id)
    form = TimetableForm(request.POST or None, instance=instance)
    context = {'form': form, 'timetable_id': timetable_id, 'page_title': 'Edit Timetable Entry'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Timetable Entry Updated Successfully")
                return redirect(reverse('manage_timetable'))
            except Exception as e:
                messages.error(request, "Could Not Update: " + str(e))
        else:
            messages.error(request, "Please fill the form properly")
    return render(request, 'hod_template/edit_timetable_template.html', context)


def delete_timetable(request, timetable_id):
    timetable = get_object_or_404(Timetable, id=timetable_id)
    try:
        timetable.delete()
        messages.success(request, "Timetable Entry Deleted Successfully")
    except Exception as e:
        messages.error(request, "Could Not Delete: " + str(e))
        
    referer = request.META.get('HTTP_REFERER')
    if referer and ('course_management' in referer or 'timetable' in referer):
        return redirect(referer)
    return redirect(reverse('manage_timetable'))


def manage_periods(request):
    periods = Period.objects.all()
    context = {
        'periods': periods,
        'page_title': 'Manage Periods'
    }
    return render(request, "hod_template/manage_periods.html", context)


def add_period(request):
    form = PeriodForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Period'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Period Added Successfully")
                return redirect(reverse('manage_periods'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Please fill the form properly")
    return render(request, 'hod_template/add_period_template.html', context)


def edit_period(request, period_id):
    instance = get_object_or_404(Period, id=period_id)
    form = PeriodForm(request.POST or None, instance=instance)
    context = {'form': form, 'period_id': period_id, 'page_title': 'Edit Period'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Period Updated Successfully")
                return redirect(reverse('manage_periods'))
            except Exception as e:
                messages.error(request, "Could Not Update: " + str(e))
        else:
            messages.error(request, "Please fill the form properly")
    return render(request, 'hod_template/edit_period_template.html', context)


def delete_period(request, period_id):
    period = get_object_or_404(Period, id=period_id)
    period.delete()
    messages.success(request, "Period Deleted Successfully")
    return redirect(reverse('manage_periods'))


def add_announcement(request):
    form = AnnouncementForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Announcement'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Announcement Added Successfully!")
                return redirect(reverse('manage_announcement'))
            except Exception as e:
                messages.error(request, "Could not Add " + str(e))
        else:
            messages.error(request, "Form has invalid data")
    return render(request, 'hod_template/add_announcement.html', context)


def manage_announcement(request):
    # Auto-delete expired announcements
    from datetime import date
    Announcement.objects.filter(expires_at__lt=date.today()).delete()
    
    announcements = Announcement.objects.all().order_by('-created_at')
    context = {
        'announcements': announcements,
        'page_title': 'Manage Announcements'
    }
    return render(request, 'hod_template/manage_announcement.html', context)


def edit_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    form = AnnouncementForm(request.POST or None, instance=announcement)
    context = {
        'form': form,
        'announcement': announcement,
        'page_title': 'Edit Announcement'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Announcement Updated Successfully!")
                return redirect(reverse('manage_announcement'))
            except Exception as e:
                messages.error(request, "Could not Update " + str(e))
        else:
            messages.error(request, "Form has invalid data")
    return render(request, 'hod_template/edit_announcement.html', context)


def delete_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    try:
        announcement.delete()
        messages.success(request, "Announcement Deleted Successfully!")
    except Exception as e:
        messages.error(request, "Could not delete: " + str(e))
        
    referer = request.META.get('HTTP_REFERER')
    if referer and ('course_management' in referer or 'announcement' in referer):
        return redirect(referer)
    return redirect(reverse('manage_announcement'))

def add_regulation(request):
    form = RegulationForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Regulation'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Regulation Added Successfully!")
                return redirect(reverse('manage_regulation'))
            except Exception as e:
                messages.error(request, "Could not Add " + str(e))
        else:
            messages.error(request, "Form has invalid data")
    return render(request, 'hod_template/add_regulation_template.html', context)


def manage_regulation(request):
    regulations = Regulation.objects.all().select_related('course', 'session').order_by('-created_at')
    context = {
        'regulations': regulations,
        'page_title': 'Manage Regulations'
    }
    return render(request, 'hod_template/manage_regulation.html', context)


def edit_regulation(request, regulation_id):
    regulation = get_object_or_404(Regulation, id=regulation_id)
    form = RegulationForm(request.POST or None, instance=regulation)
    context = {
        'form': form,
        'regulation': regulation,
        'page_title': 'Edit Regulation'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Regulation Updated Successfully!")
                return redirect(reverse('manage_regulation'))
            except Exception as e:
                messages.error(request, "Could not Update " + str(e))
        else:
            messages.error(request, "Form has invalid data")
    return render(request, 'hod_template/edit_regulation_template.html', context)


def delete_regulation(request, regulation_id):
    regulation = get_object_or_404(Regulation, id=regulation_id)
    try:
        regulation.delete()
        messages.success(request, "Regulation Deleted Successfully!")
    except Exception as e:
        messages.error(request, "Could not delete: " + str(e))
        
    referer = request.META.get('HTTP_REFERER')
    if referer and 'course_management' in referer:
        return redirect(referer)
    return redirect(reverse('manage_course_combined'))



def manage_calendar(request):
    from collections import OrderedDict
    from datetime import date as date_cls

    # Gather all current calendars
    calendars = AcademicCalendar.objects.all().select_related(
        'session', 'regulation'
    ).prefetch_related('events').order_by('-session__start_year', 'semester')

    # Group by Regulation -> Session
    reg_grouped = OrderedDict()

    # Pre-populate all regulations so empty folders are shown
    all_regulations = Regulation.objects.all().order_by('name')
    for reg in all_regulations:
        reg_grouped[reg.name] = OrderedDict()

    # Determine which (Regulation, Session) pairs to generate for
    # We now loop through all Regulations to ensure R24, R25, etc., get their semesters
    reg_session_pairs = {}
    for r in all_regulations:
        if r.session:
            key = (r.id, r.session_id)
            if key not in reg_session_pairs:
                reg_session_pairs[key] = {
                    'regulation': r,
                    'session': r.session,
                }

    # Standard set of events to pre-populate (matching the user's provided image)
    standard_event_types = [
        ('mid1', 1),
        ('mid2', 2),
        ('lab_exam', 3),
        ('end_exam', 4),
        ('next_commencement', 5)
    ]
    all_semester_keys = [s[0] for s in SEMESTER_CHOICES]  # ['1','2',..,'8']

    # For each active pair, ensure all 8 semesters exist and have standard event rows
    for (reg_id, session_id), info in reg_session_pairs.items():
        for sem_key in all_semester_keys:
            cal_obj, created = AcademicCalendar.objects.get_or_create(
                session_id=session_id,
                regulation_id=reg_id,
                semester=sem_key
            )
            
            # Add missing standard event rows if they don't exist
            existing_event_types = set(cal_obj.events.all().values_list('event_type', flat=True))
            for etype, order in standard_event_types:
                if etype not in existing_event_types:
                    CalendarEvent.objects.create(
                        calendar=cal_obj,
                        event_type=etype,
                        order=order,
                        start_date=None,
                        end_date=None
                    )

    # Re-fetch everything after generation for display
    calendars = AcademicCalendar.objects.all().select_related(
        'session', 'regulation'
    ).prefetch_related('events').order_by('-session__start_year', 'semester')

    for cal in calendars:
        reg_name = cal.regulation.name if cal.regulation else 'General'
        if reg_name not in reg_grouped:
            reg_grouped[reg_name] = OrderedDict()

        session_key = cal.session_id
        if session_key not in reg_grouped[reg_name]:
            reg_grouped[reg_name][session_key] = {
                'session': cal.session,
                'calendars': []
            }
        reg_grouped[reg_name][session_key]['calendars'].append(cal)

    context = {
        'reg_grouped': reg_grouped,
        'calendars': calendars,
        'page_title': 'Manage Academic Calendar'
    }
    return render(request, "hod_template/manage_calendar.html", context)


def add_calendar(request):
    form = AcademicCalendarForm(request.POST or None)
    formset = CalendarEventFormSet(request.POST or None, prefix='events')
    context = {
        'form': form,
        'formset': formset,
        'page_title': 'Add Academic Calendar'
    }
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            try:
                calendar = form.save()
                events = formset.save(commit=False)
                for event in events:
                    event.calendar = calendar
                    event.save()
                for obj in formset.deleted_objects:
                    obj.delete()
                messages.success(request, "Calendar Entry Added Successfully")
                return redirect(reverse('manage_calendar'))
            except Exception as e:
                messages.error(request, "Could Not Add Calendar Entry: " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly")
    return render(request, "hod_template/add_calendar_template.html", context)


def edit_calendar(request, calendar_id):
    instance = get_object_or_404(AcademicCalendar, id=calendar_id)
    form = AcademicCalendarForm(request.POST or None, instance=instance)
    formset = CalendarEventFormSet(request.POST or None, instance=instance, prefix='events')
    context = {
        'form': form,
        'formset': formset,
        'calendar_id': calendar_id,
        'page_title': 'Edit Academic Calendar'
    }
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            try:
                form.save()
                events = formset.save(commit=False)
                for event in events:
                    event.calendar = instance
                    event.save()
                for obj in formset.deleted_objects:
                    obj.delete()
                messages.success(request, "Calendar Entry Updated Successfully")
                return redirect(reverse('manage_calendar'))
            except Exception as e:
                messages.error(request, "Could Not Update Calendar: " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly")
    
    return render(request, "hod_template/edit_calendar_template.html", context)


def delete_calendar(request, calendar_id):
    calendar = get_object_or_404(AcademicCalendar, id=calendar_id)
    try:
        calendar.delete()
        messages.success(request, "Calendar Entry Deleted Successfully")
    except Exception as e:
        messages.error(request, "Could Not Delete Calendar Entry: " + str(e))
        
    referer = request.META.get('HTTP_REFERER')
    if referer and ('course_management' in referer or 'calendar' in referer):
        return redirect(referer)
    return redirect(reverse('manage_calendar'))


def inline_update_calendar(request, calendar_id):
    """AJAX endpoint to update commencement/instruction dates inline from manage_calendar view."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    try:
        from datetime import datetime
        cal = get_object_or_404(AcademicCalendar, id=calendar_id)
        field = request.POST.get('field')
        value = request.POST.get('value', '').strip()
        
        if field not in ('commencement_date', 'instruction_end_date'):
            return JsonResponse({'success': False, 'error': 'Invalid field'}, status=400)
        
        if value:
            parsed = datetime.strptime(value, '%Y-%m-%d').date()
            setattr(cal, field, parsed)
        else:
            setattr(cal, field, None)
            
        cal.save()
        
        # Format display dates safely for the frontend response
        comm_disp = cal.commencement_date.strftime('%d-%m-%Y') if cal.commencement_date else 'Not set'
        instr_end_disp = cal.instruction_end_date.strftime('%d-%m-%Y') if cal.instruction_end_date else 'Not set'
        
        combined_disp = 'Not set'
        if cal.commencement_date and cal.instruction_end_date:
            combined_disp = f"{comm_disp} to {instr_end_disp}"
        elif cal.commencement_date or cal.instruction_end_date:
            combined_disp = f"{comm_disp} / {instr_end_disp}"

        return JsonResponse({
            'success': True,
            'commencement_display': comm_disp,
            'instruction_display': combined_disp,
            'duration': cal.instruction_duration_text,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def inline_update_calendar_event(request, event_id):
    """AJAX endpoint to update a CalendarEvent's start/end date and duration inline."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    try:
        from datetime import datetime
        event = get_object_or_404(CalendarEvent, id=event_id)
        start_val = request.POST.get('start_date', '').strip()
        end_val = request.POST.get('end_date', '').strip()
        duration_val = request.POST.get('duration_text', '').strip()
        if start_val:
            event.start_date = datetime.strptime(start_val, '%Y-%m-%d').date()
        else:
            event.start_date = None
            
        if end_val:
            event.end_date = datetime.strptime(end_val, '%Y-%m-%d').date()
        else:
            event.end_date = None
            
        event.duration_text = duration_val
        event.save()
        
        return JsonResponse({
            'success': True,
            'date_display': event.date_range_display,
            'duration': event.duration_text or '—',
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def admin_view_marks_memo(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    results = StudentResult.objects.filter(student=student).select_related('subject')
    results_lookup = {res.subject_id: res for res in results}


    from collections import OrderedDict

    # Get all subjects for the student's course and regulation + any subject they have results for
    default_subjects = Subject.objects.filter(
        course=student.course, show_in_marks=True
    ).filter(
        Q(regulation=student.regulation) | Q(regulation__isnull=True)
    )
    result_subject_ids = StudentResult.objects.filter(student=student).values_list('subject_id', flat=True).distinct()
    all_subjects = Subject.objects.filter(
        Q(id__in=default_subjects) | Q(id__in=result_subject_ids)
    ).order_by('semester', 'order', 'name')


    # Build marks lookup: {subject_id: {exam_name: total}}
    marks_lookup = {}
    for res in results:
        if res.subject_id not in marks_lookup:
            marks_lookup[res.subject_id] = {}
        if res.exam_name:
            marks_lookup[res.subject_id][res.exam_name] = res.total
        
        # Store external and internal specifically
        if res.external_marks:
            marks_lookup[res.subject_id]['EXTERNAL'] = res.external_marks
        if res.internal_marks:
            marks_lookup[res.subject_id]['INTERNAL_OVERRIDE'] = res.internal_marks

    # Organize subjects by semester
    sem_subjects = {}
    for sem_key in ['1', '2', '3', '4', '5', '6', '7', '8']:
        sem_subjects[sem_key] = []

    for sub in all_subjects:
        res = results_lookup.get(sub.id)
        sem = res.semester if res and res.semester else (sub.semester or '1')

        if sem in sem_subjects:
            sub_marks = marks_lookup.get(sub.id, {})
            # IM calculation
            if 'INTERNAL_OVERRIDE' in sub_marks:
                im = sub_marks['INTERNAL_OVERRIDE']
            else:
                int1 = float(sub_marks.get('Mid 1', sub_marks.get('INT-1', sub_marks.get('MID-1', 0))) or 0)
                int2 = float(sub_marks.get('Mid 2', sub_marks.get('INT-2', sub_marks.get('MID-2', 0))) or 0)
                m_max = max(int1, int2)
                m_min = min(int1, int2)
                im = round((0.8 * m_max) + (0.2 * m_min))
            
            em = sub_marks.get('EXTERNAL', '')
            tot = im + (float(em) if em else 0)

            # Result Status (RS) and Grade based on TOTAL
            if em == '' and im == 0:
                status = ''
                grade = ''
            else:
                status = 'P' if tot >= 40 else 'F'

                if tot >= 90:
                    grade = 'S'
                elif tot >= 80:
                    grade = 'A'
                elif tot >= 70:
                    grade = 'B'
                elif tot >= 60:
                    grade = 'C'
                elif tot >= 50:
                    grade = 'D'
                elif tot >= 40:
                    grade = 'E'
                else:
                    grade = 'F'

            sem_subjects[sem].append({
                'name': sub.name,
                'code': sub.code or '',
                'im': im,
                'em': em,
                'tot': tot,
                'status': status,
                'grade': grade,
                'cr': sub.credits or '',
            })

    # Group into years
    years = OrderedDict()
    year_labels = {
        '1': ('I Year', '1', '2', 'I Sem', 'II Sem'),
        '2': ('II Year', '3', '4', 'I Sem', 'II Sem'),
        '3': ('III Year', '5', '6', 'I Sem', 'II Sem'),
        '4': ('IV Year', '7', '8', 'I Sem', 'II Sem'),
    }

    for yr_key, (yr_name, sem1, sem2, sem1_label, sem2_label) in year_labels.items():
        s1_list = sem_subjects.get(sem1, [])
        s2_list = sem_subjects.get(sem2, [])
        max_rows = max(len(s1_list), len(s2_list), 1)
        years[yr_name] = {
            'sem1_label': sem1_label,
            'sem2_label': sem2_label,
            'sem1': s1_list,
            'sem2': s2_list,
            'max_rows': range(max_rows),
        }

    context = {
        'student': student,
        'years': years,
        'page_title': 'Consolidate Marks Memo',
    }
    return render(request, "hod_template/admin_view_marks_memo.html", context)


def admin_edit_marks_memo(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    from collections import OrderedDict
    
    # Get all subjects for student + any subject they have results for
    default_subjects = Subject.objects.filter(
        course=student.course, show_in_marks=True
    ).filter(
        Q(regulation=student.regulation) | Q(regulation__isnull=True)
    )
    result_subject_ids = StudentResult.objects.filter(student=student).values_list('subject_id', flat=True).distinct()
    all_subjects = Subject.objects.filter(
        Q(id__in=default_subjects) | Q(id__in=result_subject_ids)
    ).order_by('semester', 'order', 'name')


    if request.method == 'POST':
        for sub in all_subjects:
            im_val = request.POST.get(f'im_{sub.id}', '')
            em_val = request.POST.get(f'em_{sub.id}', '')
            cr_val = request.POST.get(f'cr_{sub.id}', '')
            order_val = request.POST.get(f'order_{sub.id}', '')
            
            # Update Subject order weight
            if order_val != '':
                try:
                    sub.order = int(order_val)
                    sub.save()
                except (TypeError, ValueError):
                    pass
            
            # Update Subject credits
            if cr_val != '':
                sub.credits = float(cr_val)
                sub.save()
            
            # Get or create a dedicated record for consolidated internal/external marks
            res = StudentResult.objects.filter(
                student=student,
                subject=sub,
                exam_name='Final Internal',
            ).order_by('id').first()
            if not res:
                res = StudentResult(
                    student=student,
                    subject=sub,
                    exam_name='Final Internal',
                )
            if em_val != '':
                try:
                    em_float = float(em_val)
                except (TypeError, ValueError):
                    em_float = 0
                # External marks max is 70
                res.external_marks = min(em_float, 70)
            if im_val != '':
                try:
                    im_float = float(im_val)
                except (TypeError, ValueError):
                    im_float = 0
                res.internal_marks = im_float
            
            # Ensure semester is set correctly from the subject
            res.semester = sub.semester
            res.save()
            
        messages.success(request, "Marks Memo updated successfully")
        return redirect(reverse('admin_view_marks_memo', args=[student_id]))

    # Organize data for editing
    sem_data = OrderedDict()
    semester_choices_dict = dict(SEMESTER_CHOICES)
    results = StudentResult.objects.filter(student=student).select_related('subject')
    results_lookup = {res.subject_id: res for res in results}
    
    for sem_key in ['1', '2', '3', '4', '5', '6', '7', '8']:
        sem_name = semester_choices_dict.get(sem_key, f"Semester {sem_key}")
        sem_data[sem_name] = []
        
    for s in all_subjects:
        res = results_lookup.get(s.id)
        sem = res.semester if res and res.semester else (s.semester or '1')
        sem_name = semester_choices_dict.get(sem, f"Semester {sem}")
        if sem_name in sem_data:
            sem_data[sem_name].append({
                'subject': s,
                'internal_marks': res.internal_marks if res else 0,
                'external_marks': res.external_marks if res else 0,
                'credits': s.credits
            })
            
    # Remove empty sem sections
    sem_data = OrderedDict((k, v) for k, v in sem_data.items() if v)


    context = {
        'student': student,
        'sem_data': sem_data,
        'all_available_subjects': Subject.objects.filter(show_in_marks=True).order_by('name'),
        'page_title': 'Edit Marks Memo'
    }

    return render(request, "hod_template/admin_edit_marks_memo.html", context)

def admin_view_results_traditional(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    results = StudentResult.objects.filter(student=student).select_related('subject')

    from collections import OrderedDict

    # Get all subjects for the student's course and regulation
    all_subjects = Subject.objects.filter(
        course=student.course, show_in_marks=True
    ).filter(
        Q(regulation=student.regulation) | Q(regulation__isnull=True)
    ).order_by('order', 'name')

    # Build marks lookup: {subject_id: {exam_name: total}}
    marks_lookup = {}
    for res in results:
        if res.subject_id not in marks_lookup:
            marks_lookup[res.subject_id] = {}
        if res.exam_name:
            marks_lookup[res.subject_id][res.exam_name] = res.total

    # Organize subjects by semester
    sem_subjects = {}
    sem_stats = {}
    for sem_key in ['1', '2', '3', '4', '5', '6', '7', '8']:
        sem_subjects[sem_key] = []
        sem_stats[sem_key] = {'cr': 0.0, 'gp': 0.0, 'tot': 0.0, 'sub_count': 0, 'backlogs': 0}

    for sub in all_subjects:
        sem = sub.semester or student.semester or '1'
        if sem in sem_subjects:
            res = results.filter(subject=sub).filter(Q(semester=sem) | Q(semester__isnull=True)).first()
            if not res:
                res = results.filter(subject=sub).first()
            
            if res and res.internal_marks:
                im = res.internal_marks
            else:
                sub_marks = marks_lookup.get(sub.id, {})
                int1 = float(sub_marks.get('Mid 1', sub_marks.get('INT-1', sub_marks.get('MID-1', 0))) or 0)
                int2 = float(sub_marks.get('Mid 2', sub_marks.get('INT-2', sub_marks.get('MID-2', 0))) or 0)
                m_max = max(int1, int2)
                m_min = min(int1, int2)
                im = round((0.8 * m_max) + (0.2 * m_min))

            em = res.external_marks if res else ''
            tot = im + (float(em) if em else 0)

            if em == '' and im == 0:
                status = ''
                grade = ''
            else:
                status = 'Pass' if tot >= 40 else 'Fail'
                if tot >= 90: grade = 'S'
                elif tot >= 80: grade = 'A'
                elif tot >= 70: grade = 'B'
                elif tot >= 60: grade = 'C'
                elif tot >= 50: grade = 'D'
                elif tot >= 40: grade = 'E'
                else: grade = 'F'
                
                grade_points = {'S': 10, 'A': 9, 'B': 8, 'C': 7, 'D': 6, 'E': 5, 'F': 0}
                gp_weight = grade_points.get(grade, 0)
                cr_val = float(sub.credits or 0)
                
                sem_stats[sem]['cr'] += cr_val
                sem_stats[sem]['gp'] += gp_weight * cr_val
                sem_stats[sem]['tot'] += tot
                sem_stats[sem]['sub_count'] += 1
                if status == 'Fail':
                    sem_stats[sem]['backlogs'] += 1

            sem_subjects[sem].append({
                'name': sub.name,
                'code': sub.code or '',
                'subject_id': sub.id,
                'im': im,
                'em': em,
                'tot': tot,
                'status': status,
                'grade': grade,
                'cr': sub.credits or '',
            })

    for sk in sem_stats:
        s = sem_stats[sk]
        s['sgpa'] = round(s['gp'] / s['cr'], 2) if s['cr'] > 0 else 0.00
        s['percentage'] = round(s['tot'] / s['sub_count'], 1) if s['sub_count'] > 0 else 0.0

    semester_labels_short = {
        '1': '1-1 Sem', '2': '1-2 Sem', '3': '2-1 Sem', '4': '2-2 Sem',
        '5': '3-1 Sem', '6': '3-2 Sem', '7': '4-1 Sem', '8': '4-2 Sem'
    }

    semester_labels = {
        '1': 'I B.Tech. I Sem.', '2': 'I B.Tech. II Sem.', '3': 'II B.Tech. I Sem.', '4': 'II B.Tech. II Sem.',
        '5': 'III B.Tech. I Sem.', '6': 'III B.Tech. II Sem.', '7': 'IV B.Tech. I Sem.', '8': 'IV B.Tech. II Sem.',
    }

    # Check if current user is admin
    is_admin = request.user.is_authenticated and str(request.user.user_type) == '1'

    context = {
        'student': student,
        'sem_subjects': sem_subjects,
        'sem_stats': sem_stats,
        'semester_labels_short': semester_labels_short,
        'semester_labels': semester_labels,
        'page_title': 'Sem-wise Results',
        'is_admin': is_admin,
    }
    return render(request, "student_template/student_view_results_traditional.html", context)



def admin_add_marks_memo_subject(request, student_id):
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        semester = request.POST.get('semester')
        if subject_id and semester:
            student = get_object_or_404(Student, id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)
            # Create a StudentResult entry or update if exists
            res, created = StudentResult.objects.get_or_create(
                student=student,
                subject=subject,
                exam_name='Final Internal',
                defaults={'semester': semester}
            )
            if created:
                messages.success(request, f"Subject {subject.name} added to Marks Memo.")
            else:
                messages.info(request, f"Subject {subject.name} already exists in Marks Memo.")
        else:
            messages.error(request, "Invalid data.")
    return redirect(reverse('admin_edit_marks_memo', args=[student_id]))

def admin_delete_marks_memo_subject(request, student_id, subject_id):
    student = get_object_or_404(Student, id=student_id)
    subject = get_object_or_404(Subject, id=subject_id)
    # Delete results for this student and subject
    deleted_count, _ = StudentResult.objects.filter(student=student, subject=subject).delete()
    if deleted_count > 0:
        messages.success(request, f"Subject {subject.name} removed from Marks Memo.")
    else:
        messages.warning(request, f"No results found for {subject.name}.")
    return redirect(reverse('admin_edit_marks_memo', args=[student_id]))


def calculate_final_internal(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed")
    
    course_id = request.POST.get('course')
    session_id = request.POST.get('session')
    semester = request.POST.get('semester')
    section = request.POST.get('section')
    regulation_id = request.POST.get('regulation')
    
    if not course_id or not session_id:
        messages.error(request, "Please select Branch and Academic Year")
        return redirect(reverse('admin_view_marks_report'))
        
    # Get subjects for this filter
    subjects_qs = Subject.objects.filter(course_id=course_id)
    if semester:
        subjects_qs = subjects_qs.filter(semester=semester)
    if regulation_id:
        subjects_qs = subjects_qs.filter(regulation_id=regulation_id)
    
    subjects = list(subjects_qs)
    
    # Get students
    student_qs = Student.objects.filter(course_id=course_id)
    if section:
        student_qs = student_qs.filter(section=section)
    if semester:
        student_qs = student_qs.filter(semester=semester)
    if regulation_id:
        student_qs = student_qs.filter(regulation_id=regulation_id)
        
    students = list(student_qs)
    
    if not subjects or not students:
        messages.warning(request, "No students or subjects found for the selected criteria.")
        return redirect(reverse('admin_view_marks_report'))
        
    final_count = 0
    for student in students:
        for subject in subjects:
            # Get Mid 1 and Mid 2 results
            mid1 = StudentResult.objects.filter(student=student, subject=subject, exam_name='Mid 1').first()
            mid2 = StudentResult.objects.filter(student=student, subject=subject, exam_name='Mid 2').first()
            
            if mid1 or mid2:
                m1_total = mid1.total if mid1 else 0
                m2_total = mid2.total if mid2 else 0
                
                # Formula: Final = Round(max(m1, m2)*0.8 + min(m1, m2)*0.2)
                best = max(m1_total, m2_total)
                other = min(m1_total, m2_total)
                
                final_val = (best * 0.8) + (other * 0.2)
                rounded_final = round(final_val)
                
                # Update or create Final Internal record
                StudentResult.objects.update_or_create(
                    student=student,
                    subject=subject,
                    exam_name='Final Internal',
                    defaults={
                        'total': rounded_final,
                        'internal_marks': rounded_final, # Sync internal_marks too
                        'semester': semester or subject.semester
                    }
                )
                final_count += 1
                
    messages.success(request, f"Successfully calculated Final Internal marks for {final_count} student-subject records.")
    
    # Redirect back with the same GET parameters to show the results
    query_params = request.POST.urlencode()
    return redirect(f"{reverse('admin_view_marks_report')}?{query_params}")


def ajax_update_student_mark(request):
    """AJAX endpoint to update a student's INT or EXT mark inline from the results page."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    # Only admin can edit
    if not request.user.is_authenticated or str(request.user.user_type) != '1':
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    try:
        student_id = request.POST.get('student_id')
        subject_id = request.POST.get('subject_id')
        field = request.POST.get('field')  # 'internal_marks' or 'external_marks'
        value = request.POST.get('value', '').strip()

        if field not in ('internal_marks', 'external_marks'):
            return JsonResponse({'success': False, 'error': 'Invalid field'}, status=400)

        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)

        # Parse value
        if value == '' or value == '-':
            parsed_value = 0
        else:
            parsed_value = float(value)

        # Clamp: IM max 30, EM max 70
        if field == 'internal_marks':
            parsed_value = max(0, min(parsed_value, 30))
        else:
            parsed_value = max(0, min(parsed_value, 70))

        # Get or create the "Final Internal" result record
        sem = subject.semester or '1'
        res, created = StudentResult.objects.get_or_create(
            student=student,
            subject=subject,
            exam_name='Final Internal',
            defaults={'semester': sem}
        )

        setattr(res, field, parsed_value)
        res.semester = sem
        res.save()

        # Recalculate derived values
        im = float(res.internal_marks or 0)
        em = float(res.external_marks or 0)
        tot = im + em

        # Grade calculation
        if em == 0 and im == 0:
            status = ''
            grade = ''
        else:
            status = 'Pass' if tot >= 40 else 'Fail'
            if tot >= 90: grade = 'S'
            elif tot >= 80: grade = 'A'
            elif tot >= 70: grade = 'B'
            elif tot >= 60: grade = 'C'
            elif tot >= 50: grade = 'D'
            elif tot >= 40: grade = 'E'
            else: grade = 'F'

        # Recalculate SGPA for this semester
        grade_points_map = {'S': 10, 'A': 9, 'B': 8, 'C': 7, 'D': 6, 'E': 5, 'F': 0}

        # Get all subjects for this semester
        all_subjects = Subject.objects.filter(
            course=student.course, show_in_marks=True, semester=sem
        ).filter(
            Q(regulation=student.regulation) | Q(regulation__isnull=True)
        ).order_by('order', 'name')

        all_results = StudentResult.objects.filter(student=student).select_related('subject')
        marks_lookup = {}
        for r in all_results:
            if r.subject_id not in marks_lookup:
                marks_lookup[r.subject_id] = {}
            if r.exam_name:
                marks_lookup[r.subject_id][r.exam_name] = r.total

        sem_cr = 0.0
        sem_gp = 0.0
        sem_tot = 0.0
        sem_sub_count = 0
        sem_backlogs = 0

        for sub in all_subjects:
            sub_res = all_results.filter(subject=sub).filter(
                Q(semester=sem) | Q(semester__isnull=True)
            ).first()
            if not sub_res:
                sub_res = all_results.filter(subject=sub).first()

            if sub_res and sub_res.internal_marks:
                s_im = float(sub_res.internal_marks)
            else:
                sub_marks = marks_lookup.get(sub.id, {})
                int1 = float(sub_marks.get('Mid 1', sub_marks.get('INT-1', sub_marks.get('MID-1', 0))) or 0)
                int2 = float(sub_marks.get('Mid 2', sub_marks.get('INT-2', sub_marks.get('MID-2', 0))) or 0)
                m_max = max(int1, int2)
                m_min = min(int1, int2)
                s_im = round((0.8 * m_max) + (0.2 * m_min))

            s_em = float(sub_res.external_marks) if sub_res and sub_res.external_marks else 0
            s_tot = s_im + s_em

            if s_em == 0 and s_im == 0:
                continue

            s_status = 'Pass' if s_tot >= 40 else 'Fail'
            if s_tot >= 90: s_grade = 'S'
            elif s_tot >= 80: s_grade = 'A'
            elif s_tot >= 70: s_grade = 'B'
            elif s_tot >= 60: s_grade = 'C'
            elif s_tot >= 50: s_grade = 'D'
            elif s_tot >= 40: s_grade = 'E'
            else: s_grade = 'F'

            cr_val = float(sub.credits or 0)
            gp_weight = grade_points_map.get(s_grade, 0)
            sem_cr += cr_val
            sem_gp += gp_weight * cr_val
            sem_tot += s_tot
            sem_sub_count += 1
            if s_status == 'Fail':
                sem_backlogs += 1

        sgpa = round(sem_gp / sem_cr, 2) if sem_cr > 0 else 0.00
        percentage = round(sem_tot / sem_sub_count, 1) if sem_sub_count > 0 else 0.0

        return JsonResponse({
            'success': True,
            'im': int(im) if im == int(im) else im,
            'em': int(em) if em == int(em) else em,
            'tot': int(tot) if tot == int(tot) else tot,
            'grade': grade,
            'status': status,
            'sgpa': sgpa,
            'percentage': percentage,
            'backlogs': sem_backlogs,
            'sem_key': sem,
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
