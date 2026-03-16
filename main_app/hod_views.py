import json
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
    Admin, Internship, Staff, Student, Subject, Course, Session, Degree,
    Attendance, AttendanceReport, LeaveReportStudent, LeaveReportStaff,
    FeedbackStudent, FeedbackStaff, NotificationStaff, NotificationStudent,
    StudentResult, Period, Timetable, Assignment, AssignmentSubmission,
    Announcement, Regulation, AcademicCalendar, CalendarEvent, SEMESTER_CHOICES, StudentCertificate,
    AcademicLevel, AcademicSemester,
    EmailTemplate, Workflow, WorkflowExecutionLog
)


def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.all().count()
    subjects = Subject.objects.all()
    total_subject = subjects.count()
    total_course = Course.objects.all().count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name[:7])
        attendance_list.append(attendance_count)

    # Total Subjects and students in Each Course
    course_all = Course.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    for course in course_all:
        subjects = Subject.objects.filter(course_id=course.id).count()
        students = Student.objects.filter(course_id=course.id).count()
        course_name_list.append(course.name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)
    
    subject_all = Subject.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        course = Course.objects.get(id=subject.course.id)
        student_count = Student.objects.filter(course_id=course.id).count()
        subject_list.append(subject.name)
        student_count_list_in_subject.append(student_count)


    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Student.objects.all()
    for student in students:
        
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leave = LeaveReportStudent.objects.filter(student_id=student.id, status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leave+absent)
        student_name_list.append(student.admin.first_name)

    # Today's Absentees
    today = date.today()
    today_attendance = Attendance.objects.filter(date=today)
    today_absentees = []
    for att in today_attendance:
        absent_reports = AttendanceReport.objects.filter(attendance=att, status=False)
        for report in absent_reports:
            today_absentees.append({
                'student_name': report.student.admin.first_name + ' ' + report.student.admin.last_name,
                'roll_number': report.student.roll_number or 'N/A',
                'course': report.student.course.name if report.student.course else 'N/A',
                'subject': att.subject.name,
            })

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
        "today_date": today,
        "total_internships": Internship.objects.all().count(),
        "total_degrees": Degree.objects.all().count(),
    }

    # Recent Activities
    recent_students = Student.objects.all().order_by("-admin__created_at")[:3]
    recent_staff = Staff.objects.all().order_by("-admin__created_at")[:3]
    recent_internships = Internship.objects.all().order_by("-created_at")[:3]
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
    for i in recent_internships:
        activities.append({
            'type': 'internship',
            'title': f"Internship Posted: {i.title} @ {i.company}",
            'time': i.created_at,
            'icon': 'fa-briefcase',
            'color': 'warning'
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
    return render(request, 'hod_template/home_content.html', context)


def add_staff(request):
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
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name, profile_pic=passport_url)
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
                    email=email, password=password, user_type=3, first_name=first_name, last_name=last_name, profile_pic=passport)
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
    degree.delete()
    messages.success(request, "Course Deleted Successfully")
    return redirect(reverse('manage_degree'))


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
    year.delete()
    messages.success(request, "Year Deleted Successfully")
    return redirect(reverse('manage_year'))


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
    semester.delete()
    messages.success(request, "Semester Deleted Successfully")
    return redirect(reverse('manage_semester'))


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
    course.delete()
    messages.success(request, "Branch Deleted Successfully")
    return redirect(reverse('manage_course'))


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
    allStaff = CustomUser.objects.filter(user_type=2)
    context = {
        'allStaff': allStaff,
        'page_title': 'Manage Staff'
    }
    return render(request, "hod_template/manage_staff.html", context)


def manage_student(request):
    enrollment_number = request.GET.get('enrollment_number')
    name = request.GET.get('name')
    semester = request.GET.get('semester')
    course_id = request.GET.get('course')
    regulation_id = request.GET.get('regulation')

    students = CustomUser.objects.filter(user_type=3)

    if enrollment_number:
        students = students.filter(student__roll_number__icontains=enrollment_number)
    if name:
        students = students.filter(models.Q(first_name__icontains=name) | models.Q(last_name__icontains=name))
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
    context = {
        'student': student,
        'certificates': certificates,
        'page_title': 'View Student Details'
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


@csrf_exempt
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


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def student_feedback_message(request):
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


@csrf_exempt
def staff_feedback_message(request):
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


@csrf_exempt
def view_staff_leave(request):
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


@csrf_exempt
def view_student_leave(request):
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
        'page_title': 'View Attendance'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
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
    staff = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Send Notifications To Staff",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)


def admin_notify_student(request):
    student = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Send Notifications To Students",
        'students': student
    }
    return render(request, "hod_template/student_notification.html", context)


@csrf_exempt
def send_student_notification(request):
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


@csrf_exempt
def send_staff_notification(request):
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
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse('manage_staff'))


def delete_student(request, student_id):
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


def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        course.delete()
        messages.success(request, "Branch deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some students are assigned to this branch already. Kindly change the affected student branch and try again")
    return redirect(reverse('manage_course'))


def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, "Subject deleted successfully!")
    return redirect(reverse('manage_subject'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Academic Year deleted successfully!")
    except Exception:
        messages.error(
            request, "There are students assigned to this Academic Year. Please move them to another Academic Year.")
    return redirect(reverse('manage_session'))

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
                        user_type=3, 
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
    timetable.delete()
    messages.success(request, "Timetable Entry Deleted Successfully")
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
    return redirect(reverse('manage_regulation'))

def manage_internship(request):
    internships = Internship.objects.all().order_by('-created_at')
    context = {
        'internships': internships,
        'page_title': 'Manage Internships'
    }
    return render(request, "hod_template/manage_internship.html", context)


def add_internship(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        company = request.POST.get('company')
        description = request.POST.get('description')
        link = request.POST.get('link')
        deadline = request.POST.get('deadline')
        
        try:
            internship = Internship(
                title=title,
                company=company,
                description=description,
                link=link,
                deadline=deadline
            )
            internship.save()
            messages.success(request, "Internship Added Successfully")
            return redirect(reverse('manage_internship'))
        except Exception as e:
            messages.error(request, "Could Not Add Internship: " + str(e))
            
    context = {
        'page_title': 'Add Internship'
    }
    return render(request, "hod_template/add_internship_template.html", context)


def edit_internship(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)
    if request.method == 'POST':
        internship.title = request.POST.get('title')
        internship.company = request.POST.get('company')
        internship.description = request.POST.get('description')
        internship.link = request.POST.get('link')
        internship.deadline = request.POST.get('deadline')
        
        try:
            internship.save()
            messages.success(request, "Internship Updated Successfully")
            return redirect(reverse('manage_internship'))
        except Exception as e:
            messages.error(request, "Could Not Update Internship: " + str(e))
            
    context = {
        'internship': internship,
        'page_title': 'Edit Internship'
    }
    return render(request, "hod_template/edit_internship_template.html", context)


def delete_internship(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)
    try:
        internship.delete()
        messages.success(request, "Internship Deleted Successfully")
    except Exception as e:
        messages.error(request, "Could Not Delete Internship: " + str(e))
    return redirect(reverse('manage_internship'))

def manage_calendar(request):
    calendars = AcademicCalendar.objects.all().select_related(
        'session', 'regulation'
    ).prefetch_related('events').order_by('-session__start_year', 'semester')
    
    # Group calendars by session
    from collections import OrderedDict
    grouped = OrderedDict()
    for cal in calendars:
        session_key = cal.session_id
        if session_key not in grouped:
            grouped[session_key] = {
                'session': cal.session,
                'calendars': []
            }
        grouped[session_key]['calendars'].append(cal)
    
    context = {
        'grouped_calendars': grouped,
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
    return redirect(reverse('manage_calendar'))


def admin_view_marks_memo(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    results = StudentResult.objects.filter(student=student).select_related('subject')

    from django.db.models import Q
    from collections import OrderedDict

    # Get all subjects for the student's course and regulation
    all_subjects = Subject.objects.filter(
        course=student.course, show_in_marks=True
    ).filter(
        Q(regulation=student.regulation) | Q(regulation__isnull=True)
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
        sem = sub.semester or '1'
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
    from django.db.models import Q
    from collections import OrderedDict
    
    # Get all subjects for student
    all_subjects = Subject.objects.filter(
        course=student.course, show_in_marks=True
    ).filter(
        Q(regulation=student.regulation) | Q(regulation__isnull=True)
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
                exam_name='FINAL_EXTERNAL',
            ).order_by('id').first()
            if not res:
                res = StudentResult(
                    student=student,
                    subject=sub,
                    exam_name='FINAL_EXTERNAL',
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
    
    for sem_key in ['1', '2', '3', '4', '5', '6', '7', '8']:
        sem_name = semester_choices_dict.get(sem_key, f"Semester {sem_key}")
        subs = all_subjects.filter(semester=sem_key)
        
        sem_subs = []
        for s in subs:
            res = StudentResult.objects.filter(student=student, subject=s).first()
            sem_subs.append({
                'subject': s,
                'internal_marks': res.internal_marks if res else 0,
                'external_marks': res.external_marks if res else 0,
                'credits': s.credits
            })
        
        if sem_subs:
            sem_data[sem_name] = sem_subs

    context = {
        'student': student,
        'sem_data': sem_data,
        'page_title': 'Edit Marks Memo'
    }
    return render(request, "hod_template/admin_edit_marks_memo.html", context)
