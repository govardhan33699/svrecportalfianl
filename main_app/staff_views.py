import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *
from . import forms, models
from datetime import date

def staff_home(request):
    staff = get_object_or_404(Staff, admin=request.user)
    total_students = Student.objects.filter(course=staff.course).count()
    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()
    subjects = Subject.objects.filter(staff=staff)
    total_subject = subjects.count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name)
        attendance_list.append(attendance_count)
    context = {
        'page_title': 'Staff Panel - ' + str(staff.admin.first_name) + ' ' + str(staff.admin.last_name[0]) + '' + ' (' + str(staff.course) + ')',
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list
    }
    return render(request, "staff_template/erpnext_staff_home.html", context)


def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    courses = Course.objects.all()
    sections = Student.SECTION
    semesters = Student.SEMESTER_CHOICES
    
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'courses': courses,
        'sections': sections,
        'semesters': semesters,
        'page_title': 'Take Attendance'
    }

    return render(request, 'staff_template/staff_take_attendance.html', context)

@csrf_exempt
def get_faculty_attendance_grid(request):
    staff = get_object_or_404(Staff, admin=request.user)
    date_str = request.POST.get('date')
    
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_name = date_obj.strftime('%A')
        
        periods = Period.objects.all().order_by('number')
        timetable = Timetable.objects.filter(staff=staff, day=day_name).select_related('subject', 'course', 'period')
        
        # Attendance already taken today for this staff
        attendance_taken = Attendance.objects.filter(date=date_obj, subject__staff=staff).select_related('subject', 'period')
        taken_map = {(a.subject_id, a.period_id): True for a in attendance_taken}
        
        grid_data = []
        for p in periods:
            # Find timetable entry for this period
            entry = timetable.filter(period=p).first()
            status = "no_class"
            subject_name = ""
            subject_id = ""
            course_name = ""
            section = ""
            
            if entry:
                subject_name = entry.subject.name
                subject_id = entry.subject.id
                course_name = entry.course.name
                section = entry.section
                if taken_map.get((entry.subject_id, p.id)):
                    status = "completed"
                else:
                    status = "pending"
            
            grid_data.append({
                'period_id': p.id,
                'period_number': p.number,
                'start_time': p.start_time.strftime('%H:%M'),
                'end_time': p.end_time.strftime('%H:%M'),
                'status': status,
                'subject_name': subject_name,
                'subject_id': subject_id,
                'course_name': course_name,
                'section': section
            })
            
        return JsonResponse(json.dumps(grid_data), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def get_students(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        section = request.POST.get('section')
        semester = request.POST.get('semester')
        students = Student.objects.filter(
            course_id=subject.course.id, session=session)
        if section:
            students = students.filter(section=section)
        if semester:
            students = students.filter(semester=semester)
        student_data = []
        for student in students:
            data = {
                    "id": student.id,
                    "name": student.admin.last_name + " " + student.admin.first_name,
                    "roll_number": student.roll_number
                    }
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def save_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    period_id = request.POST.get('period')
    students = json.loads(student_data)
    try:
        session = get_object_or_404(Session, id=session_id)
        subject = get_object_or_404(Subject, id=subject_id)
        period = get_object_or_404(Period, id=period_id) if period_id else None
        
        attendance = Attendance(session=session, subject=subject, date=date, period=period)
        attendance.save()

        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict.get('id'))
            attendance_report = AttendanceReport(student=student, attendance=attendance, status=student_dict.get('status'))
            attendance_report.save()
    except Exception as e:
        return HttpResponse(str(e))

    return HttpResponse("OK")


def staff_update_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Update Attendance'
    }

    return render(request, 'staff_template/staff_update_attendance.html', context)


@csrf_exempt
def get_student_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        student_data = []
        for attendance in attendance_data:
            data = {"id": attendance.student.admin.id,
                    "name": attendance.student.admin.last_name + " " + attendance.student.admin.first_name,
                    "roll_number": attendance.student.roll_number,
                    "status": attendance.status}
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def update_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    students = json.loads(student_data)
    try:
        attendance = get_object_or_404(Attendance, id=date)

        for student_dict in students:
            student = get_object_or_404(
                Student, admin_id=student_dict.get('id'))
            attendance_report = get_object_or_404(AttendanceReport, student=student, attendance=attendance)
            attendance_report.status = student_dict.get('status')
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_apply_leave(request):
    form = LeaveReportStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff),
        'page_title': 'Apply for Leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('staff_apply_leave'))
            except Exception:
                messages.error(request, "Could not apply!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_apply_leave.html", context)


def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStaff.objects.filter(staff=staff),
        'page_title': 'Add Feedback'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Feedback submitted for review")
                return redirect(reverse('staff_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_feedback.html", context)


def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None,instance=staff)
    context = {'form': form, 'page_title': 'View/Update Profile'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = staff.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    admin.profile_pic = passport
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                staff.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('staff_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
                return render(request, "staff_template/staff_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


def staff_add_result(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff=staff)
    courses = Course.objects.all()
    sections = Student.SECTION
    semesters = Student.SEMESTER_CHOICES
    exam_choices = ["MID I", "MID II", "Assignment", "External"]
    sessions = Session.objects.all()
    
    context = {
        'page_title': 'Marks Upload',
        'subjects': subjects,
        'sessions': sessions,
        'courses': courses,
        'sections': sections,
        'semesters': semesters,
        'exam_choices': exam_choices
    }
    if request.method == 'POST':
        try:
            student_ids = request.POST.getlist('student_ids[]')
            subject_id = request.POST.get('subject')
            exam_name = request.POST.get('exam_name')
            subject = get_object_or_404(Subject, id=subject_id)

            for student_id in student_ids:
                test = request.POST.get('test_' + student_id)
                exam = request.POST.get('exam_' + student_id)
                student = get_object_or_404(Student, id=student_id)
                
                try:
                    data = StudentResult.objects.get(
                        student=student, subject=subject, exam_name=exam_name)
                    data.exam = exam
                    data.test = test
                    data.save()
                except StudentResult.DoesNotExist:
                    result = StudentResult(student=student, subject=subject, test=test, exam=exam, exam_name=exam_name)
                    result.save()
            
            messages.success(request, "Marks Saved Successfully")
        except Exception as e:
            messages.warning(request, "Error Occured While Processing Form: " + str(e))
    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_student_result(request):
    try:
        subject_id = request.POST.get('subject')
        student_id = request.POST.get('student')
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        result = StudentResult.objects.get(student=student, subject=subject)
        result_data = {
            'exam': result.exam,
            'test': result.test
        }
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        return HttpResponse('False')

#library
def add_book(request):
    if request.method == "POST":
        name = request.POST['name']
        author = request.POST['author']
        isbn = request.POST['isbn']
        category = request.POST['category']


        books = Book.objects.create(name=name, author=author, isbn=isbn, category=category )
        books.save()
        alert = True
        return render(request, "staff_template/add_book.html", {'alert':alert})
    context = {
        'page_title': "Add Book"
    }
    return render(request, "staff_template/add_book.html",context)

#issue book


def issue_book(request):
    form = forms.IssueBookForm()
    if request.method == "POST":
        form = forms.IssueBookForm(request.POST)
        if form.is_valid():
            obj = models.IssuedBook()
            obj.student_id = request.POST['name2']
            obj.isbn = request.POST['isbn2']
            obj.save()
            alert = True
            return render(request, "staff_template/issue_book.html", {'obj':obj, 'alert':alert})
    return render(request, "staff_template/issue_book.html", {'form':form})

def view_issued_book(request):
    issuedBooks = IssuedBook.objects.all()
    details = []
    for i in issuedBooks:
        days = (date.today()-i.issued_date)
        d=days.days
        fine=0
        if d>14:
            day=d-14
            fine=day*5
        books = list(models.Book.objects.filter(isbn=i.isbn))
        # students = list(models.Student.objects.filter(admin=i.admin))
        i=0
        for l in books:
            t=(books[i].name,books[i].isbn,issuedBooks[0].issued_date,issuedBooks[0].expiry_date,fine)
            i=i+1
            details.append(t)
    return render(request, "staff_template/view_issued_book.html", {'issuedBooks':issuedBooks, 'details':details})


def staff_create_assignment(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff=staff)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                assignment = form.save(commit=False)
                assignment.staff = staff
                assignment.save()
                messages.success(request, "Assignment Created Successfully")
                return redirect(reverse('staff_manage_assignments'))
            except Exception as e:
                messages.error(request, "Could Not Create Assignment: " + str(e))
        else:
            messages.error(request, "Please fill the form properly")
    else:
        form = AssignmentForm()
    # Filter subjects to only staff's subjects
    form.fields['subject'].queryset = subjects
    context = {
        'form': form,
        'page_title': 'Create Assignment'
    }
    return render(request, "staff_template/staff_create_assignment.html", context)


def staff_manage_assignments(request):
    staff = get_object_or_404(Staff, admin=request.user)
    assignments = Assignment.objects.filter(staff=staff).order_by('-created_at')
    context = {
        'assignments': assignments,
        'page_title': 'Manage Assignments'
    }
    return render(request, "staff_template/staff_manage_assignments.html", context)


def staff_view_submissions(request, assignment_id):
    staff = get_object_or_404(Staff, admin=request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id, staff=staff)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment)
    context = {
        'assignment': assignment,
        'submissions': submissions,
        'page_title': f'Submissions - {assignment.title}'
    }
    return render(request, "staff_template/staff_view_submissions.html", context)


def staff_delete_assignment(request, assignment_id):
    staff = get_object_or_404(Staff, admin=request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id, staff=staff)
    assignment.delete()
    messages.success(request, "Assignment Deleted Successfully")
    return redirect(reverse('staff_manage_assignments'))


def staff_add_timetable(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffTimetableForm(request.POST or None, staff_id=request.user.id)
    context = {
        'form': form,
        'page_title': 'Add Timetable'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Timetable Entry Added Successfully")
                return redirect(reverse('staff_manage_timetable'))
            except Exception as e:
                messages.error(request, "Could not add entry: " + str(e))
        else:
            messages.error(request, "Form has errors")
    return render(request, "staff_template/staff_add_timetable.html", context)


def staff_manage_timetable(request):
    staff = get_object_or_404(Staff, admin=request.user)
    timetables = Timetable.objects.filter(staff=staff).select_related('period', 'course', 'subject')
    
    from collections import defaultdict
    DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    periods = list(Period.objects.all().order_by('number'))

    # Build lookup: {day: {period_number: entry}}
    lookup = defaultdict(dict)
    for entry in timetables:
        lookup[entry.day][entry.period.number] = entry

    # Build grid rows: [{day, cells: [entry or None, ...]}]
    grid_rows = []
    for day in DAY_ORDER:
        cells = [lookup[day].get(p.number) for p in periods]
        grid_rows.append({'day': day, 'cells': cells})

    context = {
        'periods': periods,
        'grid_rows': grid_rows,
        'page_title': 'My Timetable'
    }
    return render(request, "staff_template/staff_manage_timetable.html", context)


def staff_view_announcement(request):
    announcements = Announcement.objects.filter(audience__in=['all', 'staff']).order_by('-created_at')
    context = {
        'announcements': announcements,
        'page_title': 'Announcements'
    }
    return render(request, "staff_template/staff_view_announcement.html", context)