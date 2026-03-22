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

from django.utils import timezone
from .models import (
    Student, Subject, Attendance, AttendanceReport, StudentResult,
    Announcement, Assignment, AssignmentSubmission, Timetable, Course,
    NotificationStudent, LeaveReportStudent, FeedbackStudent, Book, Regulation,
    Session, Period, Internship, StudyMaterial, StudentCloudFile, StudentCertificate
)
from .forms import (
    LeaveReportStudentForm, FeedbackStudentForm, StudentEditForm,
    AssignmentSubmissionForm, StudentChangePasswordForm
)


def student_home(request):
    student = get_object_or_404(Student, admin=request.user)
    import re
    current_semester_obj = student.semester
    if current_semester_obj:
        current_semester = str(current_semester_obj)
        sem_name = current_semester_obj.name
        match = re.search(r'(\d+)-(\d+)', sem_name)
        if match:
            subject_semester = str((int(match.group(1)) - 1) * 2 + int(match.group(2)))
        else:
            subject_semester = sem_name
    else:
        current_semester = '1'
        subject_semester = '1'

    current_session = student.session

    subjects = Subject.objects.filter(course=student.course, semester=subject_semester)
    total_subject = subjects.count()
    total_attendance = AttendanceReport.objects.filter(
        student=student, attendance__semester=current_semester, attendance__session=current_session, attendance__subject__in=subjects
    ).count()
    total_present = AttendanceReport.objects.filter(
        student=student, status=True, attendance__semester=current_semester, attendance__session=current_session, attendance__subject__in=subjects
    ).count()

    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        # Match report total decimal rounding calculation
        percent_present = round((total_present / total_attendance) * 100, 1)
        percent_absent = round(100 - percent_present, 1)
    subject_name = []
    data_present = []
    data_absent = []
    subjects = Subject.objects.filter(course=student.course, semester=subject_semester)

    from django.db.models import Count, Q
    attendance_stats = AttendanceReport.objects.filter(
        student=student,
        attendance__semester=current_semester,
        attendance__session=current_session
    ).values('attendance__subject').annotate(
        present=Count('id', filter=Q(status=True)),
        absent=Count('id', filter=Q(status=False))
    )
    
    stats_lookup = {item['attendance__subject']: item for item in attendance_stats}

    for subject in subjects:
        stats = stats_lookup.get(subject.id, {'present': 0, 'absent': 0})
        subject_name.append(subject.name)
        data_present.append(stats['present'])
        data_absent.append(stats['absent'])

    # Timetable for today
    from datetime import date as dt_date
    today_name = dt_date.today().strftime('%A')
    timetable_today = Timetable.objects.filter(
        course=student.course, section=student.section, day=today_name
    ).select_related('period', 'subject', 'staff').order_by('period__number')

    # Recent Activities for Student
    recent_attendance = AttendanceReport.objects.filter(
        student=student, attendance__semester=current_semester, attendance__session=current_session
    ).select_related('attendance__subject').order_by("-updated_at")[:3]
    recent_marks = StudentResult.objects.filter(student=student).select_related('subject').order_by("-updated_at")[:3]
    recent_leaves = LeaveReportStudent.objects.filter(student=student).order_by("-created_at")[:3]


    activities = []
    for att in recent_attendance:
        status = "Present" if att.status else "Absent"
        activities.append({
            'title': f"Attendance: {att.attendance.subject.name} - {status}",
            'time': att.updated_at,
            'icon': 'fa-check-circle',
            'color': 'success' if att.status else 'danger'
        })
    for mark in recent_marks:
        activities.append({
            'title': f"Marks Updated: {mark.subject.name} ({mark.exam_name})",
            'time': mark.updated_at,
            'icon': 'fa-edit',
            'color': 'primary'
        })
    for leave in recent_leaves:
        status = "Pending" if leave.status == 0 else ("Approved" if leave.status == 1 else "Rejected")
        activities.append({
            'title': f"Leave Request {status}: {leave.date}",
            'time': leave.created_at,
            'icon': 'fa-calendar-minus',
            'color': 'warning' if leave.status == 0 else ('success' if leave.status == 1 else 'danger')
        })

    activities.sort(key=lambda x: x['time'], reverse=True)

    # Upcoming assignments
    from datetime import date as dt_date2
    upcoming_assignments = Assignment.objects.filter(
        subject__course=student.course,
        due_date__gte=dt_date2.today()
    ).order_by('due_date')[:5]

    # ── CGPA Overview Calculation ──
    from django.db.models import Q
    all_results = StudentResult.objects.filter(student=student).select_related('subject')
    all_subjects = Subject.objects.filter(
        course=student.course, show_in_marks=True
    ).filter(
        Q(regulation=student.regulation) | Q(regulation__isnull=True)
    ).order_by('order', 'name')

    # Build marks lookup
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

            # Internal marks
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
    # Max marks per subject = 100 (IM + EM), so percentage = avg total
    max_cgpa = 10.0

    # Class awarded
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
        'page_title': 'Dashboard',
        'total_attendance': total_attendance,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'total_subject': total_subject,
        'data_name': subject_name,
        'data_present': data_present,
        'data_absent': data_absent,
        'recent_activities': activities[:10],
        'timetable_today': timetable_today,
        'today_name': today_name,
        'upcoming_assignments': upcoming_assignments,
        'greeting': get_greeting(),
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

    # Grouped Announcements for Latest Updates Grid
    context['news_announcements'] = Announcement.objects.filter(
        category='news'
    ).order_by('-created_at')[:5]
    
    context['exam_announcements'] = Announcement.objects.filter(
        category__in=['mid', 'sem']
    ).order_by('-created_at')[:5]
    
    context['placement_announcements'] = Announcement.objects.filter(
        category__in=['event', 'holiday', 'other', 'placement']
    ).order_by('-created_at')[:5]

    return render(request, 'student_template/erpnext_student_home.html', context)

def get_greeting():
    hour = timezone.localtime(timezone.now()).hour
    if hour < 12:
        return "Good Morning ☀️"
    elif hour < 17:
        return "Good Afternoon 🌤️"
    else:
        return "Good Evening 🌙"


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
                
                # Additional detail fields
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
    results = StudentResult.objects.filter(student=student).select_related('subject')

    # Semester display names
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

    # Exam type display order (key, display_label)
    EXAM_TYPES = [('INT-1', 'MID-1'), ('INT-2', 'MID-2')]

    # Mapping from various exam_name strings to our standard keys
    EXAM_NAME_MAP = {
        'Mid 1': 'INT-1', 'Internal 1': 'INT-1', 'MID I': 'INT-1', 'INT-1': 'INT-1', 'INT1': 'INT-1',
        'MID-1': 'INT-1', 'Mid-1': 'INT-1',
        'Mid 2': 'INT-2', 'Internal 2': 'INT-2', 'MID II': 'INT-2', 'INT-2': 'INT-2', 'INT2': 'INT-2',
        'MID-2': 'INT-2', 'Mid-2': 'INT-2',
    }

    # Build raw data: { semester_key: { subject_id: { 'name', 'code', 'max_marks', 'marks': {}, 'internal_override': None } } }
    raw = defaultdict(lambda: defaultdict(lambda: {'name': '', 'code': '', 'max_marks': 30, 'marks': {}, 'internal_override': None}))

    # First, seed ALL subjects for this student's course that match their regulation
    from django.db.models import Q
    all_subjects = Subject.objects.filter(
        course=student.course,
        show_in_marks=True
    ).filter(
        Q(regulation=student.regulation) | Q(regulation__isnull=True)
    )
    for sub in all_subjects:
        sem = sub.semester or student.semester or '1'
        entry = raw[sem][sub.id]
        entry['name'] = sub.name
        entry['code'] = sub.code or ''
        entry['max_marks'] = sub.max_marks or 30

    # Then, overlay actual marks data
    for res in results:
        # Robust semester attribution: prioritize result's semester, then fallback to subject's semester
        sem = res.semester or res.subject.semester or student.semester or '1'
        sub_id = res.subject_id
        entry = raw[sem][sub_id]
        entry['name'] = res.subject.name
        entry['code'] = res.subject.code or ''
        entry['max_marks'] = res.subject.max_marks or 30

        # Capture internal override if present
        if res.internal_marks:
            entry['internal_override'] = res.internal_marks

        exam_key = EXAM_NAME_MAP.get(res.exam_name)
        if exam_key:
            entry['marks'][exam_key] = res.total

    # Build structured data for template
    # { semester_display_name: { 'subjects': [...], 'rows': [...] } }
    from collections import OrderedDict
    semester_data = OrderedDict()

    # Always show all 8 semesters in order
    for sem_key in ['1', '2', '3', '4', '5', '6', '7', '8']:
        sem_name = SEMESTER_DISPLAY.get(sem_key, f'Semester {sem_key}')
        subjects_dict = raw.get(sem_key, {})

        # Build ordered subjects list
        subjects_list = []
        subject_ids_ordered = list(subjects_dict.keys())
        for sub_id in subject_ids_ordered:
            s = subjects_dict[sub_id]
            subjects_list.append({
                'name': s['name'],
                'code': s['code'],
                'max_marks': s['max_marks'],
            })

        # Build rows for each exam type
        rows = []
        for exam_key, exam_label in EXAM_TYPES:
            marks_row = []
            for sub_id in subject_ids_ordered:
                val = subjects_dict[sub_id]['marks'].get(exam_key, '')
                marks_row.append(val)
            rows.append({'label': exam_label, 'marks': marks_row, 'is_final': False})

        # Calculate Final row
        final_marks = []
        for sub_id in subject_ids_ordered:
            s_entry = subjects_dict[sub_id]
            
            # Use override if exists
            if s_entry['internal_override'] is not None:
                final_score = round(float(s_entry['internal_override']))
            else:
                m = s_entry['marks']
                int1 = float(m.get('INT-1', 0) or 0)
                int2 = float(m.get('INT-2', 0) or 0)
                m_max = max(int1, int2)
                m_min = min(int1, int2)
                final_score = round((0.8 * m_max) + (0.2 * m_min))
            final_marks.append(final_score)
        rows.append({'label': 'Final', 'marks': final_marks, 'is_final': True})

        semester_data[sem_name] = {
            'subjects': subjects_list,
            'rows': rows,
            'has_subjects': len(subjects_list) > 0,
        }

    context = {
        'semester_data': semester_data,
        'page_title': "Internal Marks Details",
        'hide_sidebar': True,
    }
    return render(request, "student_template/student_view_marks.html", context)


def student_consolidated_marks(request):
    student = get_object_or_404(Student, admin=request.user)
    results = StudentResult.objects.filter(student=student).select_related('subject')

    from django.db.models import Q
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
    for sem_key in ['1', '2', '3', '4', '5', '6', '7', '8']:
        sem_subjects[sem_key] = []

    for sub in all_subjects:
        sem = sub.semester or student.semester or '1'
        if sem in sem_subjects:
            # Get IM (internal marks) and EM (external marks) for this subject
            # Find the result record
            # Robust lookup: match subject and either no semester or matching semester
            res = results.filter(subject=sub).filter(Q(semester=sem) | Q(semester__isnull=True)).first()
            if not res:
                res = results.filter(subject=sub).first()
            
            # Use internal_marks override if available, else calculate from mids
            if res and res.internal_marks:
                im = res.internal_marks
            else:
                sub_marks = marks_lookup.get(sub.id, {})
                # IM = best of MID-1 / MID-2 based internal calculation
                int1 = float(sub_marks.get('Mid 1', sub_marks.get('INT-1', sub_marks.get('MID-1', 0))) or 0)
                int2 = float(sub_marks.get('Mid 2', sub_marks.get('INT-2', sub_marks.get('MID-2', 0))) or 0)
                m_max = max(int1, int2)
                m_min = min(int1, int2)
                im = round((0.8 * m_max) + (0.2 * m_min))

            # Use external_marks from StudentResult if available
            # Find the result record with external marks
            res = results.filter(subject=sub).first()
            em = res.external_marks if res else ''
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

    # Group into years (each year has 2 semesters side by side)
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
        'hide_sidebar': True,
    }
    return render(request, "student_template/student_consolidated_marks.html", context)


def student_view_results_traditional(request):
    student = get_object_or_404(Student, admin=request.user)
    results = StudentResult.objects.filter(student=student).select_related('subject')

    from django.db.models import Q
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
            # Find the result record
            res = results.filter(subject=sub).filter(Q(semester=sem) | Q(semester__isnull=True)).first()
            if not res:
                res = results.filter(subject=sub).first()
            
            # Use internal_marks override if available, else calculate from mids
            if res and res.internal_marks:
                im = res.internal_marks
            else:
                sub_marks = marks_lookup.get(sub.id, {})
                int1 = float(sub_marks.get('Mid 1', sub_marks.get('INT-1', sub_marks.get('MID-1', 0))) or 0)
                int2 = float(sub_marks.get('Mid 2', sub_marks.get('INT-2', sub_marks.get('MID-2', 0))) or 0)
                m_max = max(int1, int2)
                m_min = min(int1, int2)
                im = round((0.8 * m_max) + (0.2 * m_min))

            # Use external_marks from StudentResult
            em = res.external_marks if res else ''
            tot = im + (float(em) if em else 0)

            # Result Status (RS) and Grade based on TOTAL
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
                
                # Stats calculation
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
                'im': im,
                'em': em,
                'tot': tot,
                'status': status,
                'grade': grade,
                'cr': sub.credits or '',
            })

    # Calculate final aggregate summary metrics
    for sk in sem_stats:
        s = sem_stats[sk]
        s['sgpa'] = round(s['gp'] / s['cr'], 2) if s['cr'] > 0 else 0.00
        s['percentage'] = round(s['tot'] / s['sub_count'], 1) if s['sub_count'] > 0 else 0.0

    semester_labels_short = {
        '1': '1-1 Sem', '2': '1-2 Sem', '3': '2-1 Sem', '4': '2-2 Sem',
        '5': '3-1 Sem', '6': '3-2 Sem', '7': '4-1 Sem', '8': '4-2 Sem'
    }

    semester_labels = {
        '1': 'I B.Tech. I Sem.',
        '2': 'I B.Tech. II Sem.',
        '3': 'II B.Tech. I Sem.',
        '4': 'II B.Tech. II Sem.',
        '5': 'III B.Tech. I Sem.',
        '6': 'III B.Tech. II Sem.',
        '7': 'IV B.Tech. I Sem.',
        '8': 'IV B.Tech. II Sem.',
    }

    context = {
        'student': student,
        'sem_subjects': sem_subjects,
        'sem_stats': sem_stats,
        'semester_labels_short': semester_labels_short,
        'semester_labels': semester_labels,
        'page_title': 'Results',
        'hide_sidebar': True,
    }
    return render(request, "student_template/student_view_results_traditional.html", context)#library

#materials
def student_view_material(request):
    student = get_object_or_404(Student, admin=request.user)
    # Get subjects for student's course and semester
    subjects = Subject.objects.filter(course=student.course, semester=student.semester)
    materials = StudyMaterial.objects.filter(subject__in=subjects).order_by('-created_at')
    
    context = {
        'page_title': 'Study Materials',
        'materials': materials,
        'hide_sidebar': True,
    }
    return render(request, 'student_template/student_view_material.html', context)


def student_view_timetable(request):
    student = get_object_or_404(Student, admin=request.user)
    
    # Get all periods
    periods = list(Period.objects.all().order_by('number'))
    
    # Get timetable entries matching student regulation
    filters = {'course': student.course, 'section': student.section}
    if student.regulation:
        filters['subject__regulation'] = student.regulation
        
    timetable_entries = Timetable.objects.filter(**filters).select_related(
        'period', 'subject', 'staff', 'staff__admin'
    )
    
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
    # Map assignment_id to submission object for easy lookup
    submission_map = {sub.assignment_id: sub for sub in submissions}
    context = {
        'assignments': assignments,
        'submission_map': submission_map,
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
    user = request.user
    if request.method == 'POST':
        form = StudentChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            
            email = form.cleaned_data.get('email')
            
            # Check if email is already taken by someone else
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, "Email is already taken. Please choose another one.")
                context = {'form': form, 'page_title': 'Change Password'}
                return render(request, "student_template/student_change_password.html", context)
                
            user.email = email
            
            if new_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Profile & Password Updated Successfully! Please login again.")
                return redirect(reverse('login_page'))
            else:
                user.save()
                # Update session to maintain login if password didn't change (optional but good)
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                messages.success(request, "Profile Updated Successfully!")
        else:
            messages.error(request, "Invalid form submission or passwords do not match")
    else:
        form = StudentChangePasswordForm(initial={
            'email': user.email
        })
    context = {
        'form': form,
        'page_title': 'Update Profile'
    }
    return render(request, "student_template/student_change_password.html", context)


def student_attendance_report(request):
    student = get_object_or_404(Student, admin=request.user)
    import re
    current_semester_obj = student.semester
    if current_semester_obj:
        current_semester = str(current_semester_obj)
        sem_name = current_semester_obj.name
        match = re.search(r'(\d+)-(\d+)', sem_name)
        if match:
            subject_semester = str((int(match.group(1)) - 1) * 2 + int(match.group(2)))
        else:
            subject_semester = sem_name
    else:
        current_semester = '1'
        subject_semester = '1'
        
    subjects = Subject.objects.filter(course=student.course, semester=subject_semester)



    
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
        attendance_count = AttendanceReport.objects.filter(
            attendance__subject=subject, 
            attendance__session=student.session,
            attendance__semester=current_semester,
            student=student
        ).count()
        present_count = AttendanceReport.objects.filter(
            attendance__subject=subject, 
            attendance__session=student.session,
            attendance__semester=current_semester,
            student=student, 
            status=True
        ).count()
        
        att_percent = 0
        if attendance_count > 0:
            att_percent = round((present_count / attendance_count) * 100, 2)
        
        # Determine faculty name from timetable if available, else fallback to subject default
        if subject.id in subject_staff_map and subject_staff_map[subject.id]:
            faculty_name = ", ".join(subject_staff_map[subject.id])
        elif subject.staff:
            faculty_name = f"{subject.staff.admin.first_name} {subject.staff.admin.last_name}"
        else:
            faculty_name = "Not Assigned"
            
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
    
    # Get all attendance dates for this student's course/session/semester
    attendance_records = AttendanceReport.objects.filter(
        student=student,
        attendance__semester=current_semester,
        attendance__session=student.session
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
        'hide_sidebar': True,
    }
    return render(request, "student_template/student_attendance_report.html", context)


def student_view_announcement(request):
    announcements = Announcement.objects.filter(audience__in=['all', 'student']).order_by('-created_at')
    context = {
        'announcements': announcements,
        'page_title': 'Announcements',
        'hide_sidebar': True,
    }
    return render(request, "student_template/student_view_announcement.html", context)

def student_view_internship(request):
    internships = Internship.objects.all().order_by('-created_at')
    context = {
        'internships': internships,
        'page_title': 'Internship Opportunities'
    }
    return render(request, "student_template/student_view_internship.html", context)
def student_cloud_storage(request):
    student = get_object_or_404(Student, admin=request.user)
    files = StudentCloudFile.objects.filter(student=student).order_by('-created_at')
    
    # Categorize files for easier display
    categorized_files = {
        'notes': files.filter(category='notes'),
        'pdf': files.filter(category='pdf'),
        'question_paper': files.filter(category='question_paper'),
        'important': files.filter(category='important'),
    }
    
    context = {
        'files': files,
        'categorized_files': categorized_files,
        'page_title': 'Cloud Storage'
    }
    return render(request, "student_template/student_cloud_storage.html", context)


def student_upload_file(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method")
    
    try:
        student = get_object_or_404(Student, admin=request.user)
        title = request.POST.get("title")
        category = request.POST.get("category")
        description = request.POST.get("description")
        file = request.FILES.get("file")
        
        print(f"DEBUG: Upload attempt by {student} - Title: {title}, Category: {category}")
        
        if not file:
            messages.error(request, "Please select a file to upload.")
            return redirect(reverse('student_cloud_storage'))
            
        student_file = StudentCloudFile.objects.create(
            student=student,
            title=title if title else file.name,
            file=file,
            category=category,
            description=description
        )
        print(f"DEBUG: Successfully uploaded {student_file.title}")
        messages.success(request, "File uploaded successfully.")
    except Exception as e:
        print(f"DEBUG: Upload error: {e}")
        messages.error(request, f"Error uploading file: {e}")
        
    return redirect(reverse('student_cloud_storage'))


def student_delete_file(request, file_id):
    file = get_object_or_404(StudentCloudFile, id=file_id)
    
    # Ensure students can only delete their own files
    student = get_object_or_404(Student, admin=request.user)
    if file.student == student:
        file.file.delete() # Delete physical file
        file.delete() # Delete record
        messages.success(request, "File deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this file.")
        
    return redirect(reverse('student_cloud_storage'))
def student_view_certificates(request):
    student = get_object_or_404(Student, admin=request.user)
    certificates = StudentCertificate.objects.filter(student=student).order_by('-issue_date')
    context = {
        'certificates': certificates,
        'page_title': 'My Certificates'
    }
    return render(request, 'student_template/student_view_certificates.html', context)
