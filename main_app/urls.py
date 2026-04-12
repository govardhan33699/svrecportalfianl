"""college_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from main_app.EditResultView import EditResultView

from . import hod_views, staff_views, student_views, views

urlpatterns = [
    path("", views.login_page, name='login_page'),
    path("get_attendance", views.get_attendance, name='get_attendance'),
    path("firebase-messaging-sw.js", views.showFirebaseJS, name='showFirebaseJS'),
    path("doLogin/", views.doLogin, name='user_login'),
    path("logout_user/", views.logout_user, name='user_logout'),
    path("get_user_profile_pic/", views.get_user_profile_pic, name='get_user_profile_pic'),
    path("admin/home/", hod_views.admin_home, name='admin_home'),
    path("staff/add", hod_views.add_staff, name='add_staff'),
    path("course/add", hod_views.add_degree, name='add_degree'),
    path("academic_level/add", hod_views.add_year, name='add_year'),
    path("academic_semester/add", hod_views.add_semester, name='add_semester'),
    path("branch/add", hod_views.add_course, name='add_course'),
    path("send_student_notification/", hod_views.send_student_notification,
         name='send_student_notification'),
    path("send_staff_notification/", hod_views.send_staff_notification,
         name='send_staff_notification'),
    path("add_session/", hod_views.add_session, name='add_session'),
    path("admin_notify_student", hod_views.admin_notify_student,
         name='admin_notify_student'),
    path("admin_notify_staff", hod_views.admin_notify_staff,
         name='admin_notify_staff'),
    path("admin_view_profile", hod_views.admin_view_profile,
         name='admin_view_profile'),
    path("check_email_availability", hod_views.check_email_availability,
         name="check_email_availability"),
    path("session/manage/", hod_views.manage_session, name='manage_session'),
    path("session/edit/<int:session_id>",
         hod_views.edit_session, name='edit_session'),
    path("student/view/feedback/", hod_views.student_feedback_message,
         name="student_feedback_message",),
    path("staff/view/feedback/", hod_views.staff_feedback_message,
         name="staff_feedback_message",),
    path("student/view/leave/", hod_views.view_student_leave,
         name="view_student_leave",),
    path("staff/view/leave/", hod_views.view_staff_leave, name="view_staff_leave",),
    path("attendance/view/", hod_views.admin_view_attendance,
         name="admin_view_attendance",),
    path("marks/calculate-final/", hod_views.calculate_final_internal, name='calculate_final_internal'),
    path("marks/view/", hod_views.admin_view_marks_report,
         name="admin_view_marks_report",),
    path("attendance/fetch/", hod_views.get_admin_attendance,
         name='get_admin_attendance'),
    path("student/add/", hod_views.add_student, name='add_student'),
    path("subject/add/", hod_views.add_subject, name='add_subject'),
    path("staff/manage/", hod_views.manage_staff, name='manage_staff'),
    path("student/manage/", hod_views.manage_student, name='manage_student'),
    path("student/view/<int:student_id>/", hod_views.view_student_detail, name='view_student_detail'),
    path("student/view/<int:student_id>/marks-memo/", hod_views.admin_view_marks_memo, name='admin_view_marks_memo'),
    path("student/view/<int:student_id>/edit-memo/", hod_views.admin_edit_marks_memo, name='admin_edit_marks_memo'),
    path("student/view/<int:student_id>/add-memo-subject/", hod_views.admin_add_marks_memo_subject, name='admin_add_marks_memo_subject'),
    path("student/view/<int:student_id>/delete-memo-subject/<int:subject_id>/", hod_views.admin_delete_marks_memo_subject, name='admin_delete_marks_memo_subject'),

    path("student/view/<int:student_id>/results-traditional/", hod_views.admin_view_results_traditional, name='admin_view_results_traditional'),
    path("student/ajax-update-mark/", hod_views.ajax_update_student_mark, name='ajax_update_student_mark'),
    path("ajax-delete-entity/", hod_views.ajax_delete_entity, name='ajax_delete_entity'),
    path("student/import/", hod_views.import_student, name='import_student'),
    path("course_management/", hod_views.manage_course_combined, name='manage_course_combined'),
    path("course/manage/", hod_views.manage_degree, name='manage_degree'),
    path("academic_level/manage/", hod_views.manage_year, name='manage_year'),
    path("academic_semester/manage/", hod_views.manage_semester, name='manage_semester'),
    path("branch/manage/", hod_views.manage_course, name='manage_course'),
    path("subject/manage/", hod_views.manage_subject, name='manage_subject'),
    path("staff/edit/<int:staff_id>", hod_views.edit_staff, name='edit_staff'),
    path("staff/delete/<int:staff_id>",
         hod_views.delete_staff, name='delete_staff'),

    path("course/delete/<int:degree_id>",
         hod_views.delete_degree, name='delete_degree'),
    path("academic_level/delete/<int:year_id>",
         hod_views.delete_year, name='delete_year'),
    path("academic_semester/delete/<int:semester_id>",
         hod_views.delete_semester, name='delete_semester'),

    path("branch/delete/<int:course_id>",
         hod_views.delete_course, name='delete_course'),

    path("subject/delete/<int:subject_id>",
         hod_views.delete_subject, name='delete_subject'),

    path("session/delete/<int:session_id>",
         hod_views.delete_session, name='delete_session'),

    path("student/delete/<int:student_id>",
         hod_views.delete_student, name='delete_student'),
    path("student/edit/<int:student_id>",
         hod_views.edit_student, name='edit_student'),
    path("course/edit/<int:degree_id>",
         hod_views.edit_degree, name='edit_degree'),
    path("academic_level/edit/<int:year_id>",
         hod_views.edit_year, name='edit_year'),
    path("academic_semester/edit/<int:semester_id>",
         hod_views.edit_semester, name='edit_semester'),
    path("branch/edit/<int:course_id>",
         hod_views.edit_course, name='edit_course'),
    path("subject/edit/<int:subject_id>",
         hod_views.edit_subject, name='edit_subject'),


    # Staff
    path("staff/home/", staff_views.staff_home, name='staff_home'),
    path("staff/apply/leave/", staff_views.staff_apply_leave,
         name='staff_apply_leave'),
    path("staff/feedback/", staff_views.staff_feedback, name='staff_feedback'),
    path("staff/view/profile/", staff_views.staff_view_profile,
         name='staff_view_profile'),
    path("staff/attendance/take/", staff_views.staff_take_attendance,
         name='staff_take_attendance'),
    path("staff/attendance/update/", staff_views.staff_update_attendance,
         name='staff_update_attendance'),
    path("staff/attendance/grid/", staff_views.get_faculty_attendance_grid, name='get_faculty_attendance_grid'),
    path("staff/get_students/", staff_views.get_students, name='get_students'),
    path("staff/materials/add/", staff_views.staff_add_material, name="staff_add_material"),



    path("staff/attendance/fetch/", staff_views.get_student_attendance,
         name='get_student_attendance'),
    path("staff/attendance/save/",
         staff_views.save_attendance, name='save_attendance'),
    path("staff/attendance/update_save/",
         staff_views.update_attendance, name='update_attendance'),
    path("staff/fcmtoken/", staff_views.staff_fcmtoken, name='staff_fcmtoken'),
    path("staff/view/notification/", staff_views.staff_view_notification,
         name="staff_view_notification"),
    path("staff/result/add/", staff_views.staff_add_result, name='staff_add_result'),
    path("staff/result/edit/", EditResultView.as_view(),
         name='edit_student_result'),
    path('staff/result/fetch/', staff_views.fetch_student_result,
         name='fetch_student_result'),
    path('staff/result/export-template/', staff_views.export_marks_template, name='export_marks_template'),
    path('staff/result/generic-template/', staff_views.download_generic_template, name='download_generic_template'),
    path('staff/result/import-excel/', staff_views.import_marks_excel, name='import_marks_excel'),
    path('staff/result/export-final-internal/', staff_views.export_final_internal, name='export_final_internal'),




    # Student
    path("student/home/", student_views.student_home, name='student_home'),
    path("student/view/attendance/", student_views.student_view_attendance,
         name='student_view_attendance'),
    path("student/apply/leave/", student_views.student_apply_leave,
         name='student_apply_leave'),
    path("student/feedback/", student_views.student_feedback,
         name='student_feedback'),
    path("student/view/profile/", student_views.student_view_profile,
         name='student_view_profile'),
    path("student/fcmtoken/", student_views.student_fcmtoken,
         name='student_fcmtoken'),
     # path('student/todo',student_views.todo,name='todo'),

     
     path("student/materials/view/", student_views.student_view_material, name="student_view_material"),

    path("student/view/notification/", student_views.student_view_notification,
         name="student_view_notification"),
    path('student/view/result/', student_views.student_view_result,
         name='student_view_result'),
    path('student/consolidated-marks/', student_views.student_consolidated_marks,          name='student_consolidated_marks'),     path('student/results-traditional/', student_views.student_view_results_traditional,          name='student_view_results_traditional'),


    # Staff Timetable
    path("staff/timetable/add/", staff_views.staff_add_timetable, name='staff_add_timetable'),
    path("staff/timetable/manage/", staff_views.staff_manage_timetable, name='staff_manage_timetable'),

    # Timetable management (Admin)
    path("timetable/manage/", hod_views.manage_timetable, name='manage_timetable'),
    path("timetable/add/", hod_views.add_timetable, name='add_timetable'),
    path("timetable/edit/<int:timetable_id>", hod_views.edit_timetable, name='edit_timetable'),
    path("timetable/delete/<int:timetable_id>", hod_views.delete_timetable, name='delete_timetable'),

    # Assignment management (Staff)
    path("staff/assignment/create/", staff_views.staff_create_assignment, name='staff_create_assignment'),
    path("staff/assignment/manage/", staff_views.staff_manage_assignments, name='staff_manage_assignments'),
    path("staff/assignment/submissions/<int:assignment_id>", staff_views.staff_view_submissions, name='staff_view_submissions'),
    path("staff/assignment/grade/", staff_views.staff_grade_submission, name='staff_grade_submission'),
    path("staff/assignment/delete/<int:assignment_id>", staff_views.staff_delete_assignment, name='staff_delete_assignment'),

    # Student features
    path("student/timetable/", student_views.student_view_timetable, name='student_view_timetable'),
    path("student/assignments/", student_views.student_view_assignments, name='student_view_assignments'),
    path("student/assignment/submit/<int:assignment_id>", student_views.student_submit_assignment, name='student_submit_assignment'),
    path("student/change-password/", student_views.student_change_password, name='student_change_password'),
    path("student/attendance/report/", student_views.student_attendance_report, name='student_attendance_report'),

    # Period management (Admin) - Hidden as periods are fixed
    # path("period/manage/", hod_views.manage_periods, name='manage_periods'),
    # path("period/add/", hod_views.add_period, name='add_period'),
    # path("period/edit/<int:period_id>", hod_views.edit_period, name='edit_period'),
    # path("period/delete/<int:period_id>", hod_views.delete_period, name='delete_period'),
    
    # Announcement management
    path("announcement/manage/", hod_views.manage_announcement, name='manage_announcement'),
    path("announcement/add/", hod_views.add_announcement, name='add_announcement'),
    path("announcement/edit/<int:announcement_id>", hod_views.edit_announcement, name='edit_announcement'),
    path("announcement/delete/<int:announcement_id>", hod_views.delete_announcement, name='delete_announcement'),

    # Regulation management
    path("regulation/manage/", hod_views.manage_regulation, name='manage_regulation'),
    path("regulation/add/", hod_views.add_regulation, name='add_regulation'),
    path("regulation/edit/<int:regulation_id>", hod_views.edit_regulation, name='edit_regulation'),
    path("regulation/delete/<int:regulation_id>", hod_views.delete_regulation, name='delete_regulation'),

    # Staff View Announcement
    path("staff/announcement/view/", staff_views.staff_view_announcement, name='staff_view_announcement'),

    # Student View Announcement
    path("student/announcement/view/", student_views.student_view_announcement, name='student_view_announcement'),



    # Academic Calendar management
    path("calendar/manage/", hod_views.manage_calendar, name='manage_calendar'),
    path("calendar/add/", hod_views.add_calendar, name='add_calendar'),
    path("calendar/edit/<int:calendar_id>", hod_views.edit_calendar, name='edit_calendar'),
    path("calendar/delete/<int:calendar_id>", hod_views.delete_calendar, name='delete_calendar'),
    path("calendar/inline-update/<int:calendar_id>/", hod_views.inline_update_calendar, name='inline_update_calendar'),
    path("calendar/event/inline-update/<int:event_id>/", hod_views.inline_update_calendar_event, name='inline_update_calendar_event'),

    # Student Certificate management (Admin)
    path("student/view/<int:student_id>/certificate/add/", hod_views.add_student_certificate, name='add_student_certificate'),
    path("student/view/<int:student_id>/certificate/edit/<int:certificate_id>/", hod_views.edit_student_certificate, name='edit_student_certificate'),
    path('student/view/<int:student_id>/delete-certificate/<int:certificate_id>/', hod_views.delete_student_certificate, name="delete_student_certificate"),
    
    # Workflow Automation
    path('manage_email_templates/', hod_views.manage_email_templates, name="manage_email_templates"),
    path('add_email_template/', hod_views.add_email_template, name="add_email_template"),
    path('edit_email_template/<int:template_id>/', hod_views.edit_email_template, name="edit_email_template"),
    path('delete_email_template/<int:template_id>/', hod_views.delete_email_template, name="delete_email_template"),
    
    path('manage_workflows/', hod_views.manage_workflows, name="manage_workflows"),
    path('workflow_builder/', hod_views.workflow_builder, name="workflow_builder"),
    path('workflow_builder/<int:workflow_id>/', hod_views.workflow_builder, name="edit_workflow"),
    path('save_workflow/', hod_views.save_workflow, name="save_workflow"),
    path('delete_workflow/<int:workflow_id>/', hod_views.delete_workflow, name="delete_workflow"),

    # Student Certificates
    path("student/my-certificates/", student_views.student_view_certificates, name='student_view_certificates'),

    # Student Cloud Storage
    path("student/cloud/", student_views.student_cloud_storage, name='student_cloud_storage'),
    path("student/cloud/upload/", student_views.student_upload_file, name='student_upload_file'),
    path("student/cloud/delete/<int:file_id>/", student_views.student_delete_file, name='student_delete_file'),
]
