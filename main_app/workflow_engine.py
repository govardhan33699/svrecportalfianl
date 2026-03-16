import json
from django.core.mail import send_mail
from django.template import Context, Template
from django.conf import settings
from .models import Student, EmailTemplate, Workflow, WorkflowExecutionLog, StudentResult, AttendanceReport

class WorkflowEngine:
    def __init__(self, workflow_id, context_data=None):
        self.workflow = Workflow.objects.get(id=workflow_id)
        self.graph = self.workflow.graph_data['drawflow']['Home']['data']
        self.context_data = context_data or {}
        self.execution_logs = []

    def run(self, student_ids=None):
        """
        Executes the workflow graph.
        If student_ids is provided, it starts with those students.
        Otherwise, it starts with all students (or based on context).
        """
        if student_ids is None:
            # For triggers like 'announcement', we might start with all students
            # who are the intended audience.
            queryset = Student.objects.all()
        else:
            queryset = Student.objects.filter(id__in=student_ids)

        # Find the trigger node (node with type 'trigger')
        trigger_node_id = None
        for node_id, node_data in self.graph.items():
            if node_data['name'] == 'trigger_start':
                trigger_node_id = node_id
                break
        
        if not trigger_node_id:
            print(f"No trigger node found for workflow {self.workflow.id}")
            return

        # Start traversal from trigger node
        self.process_node(trigger_node_id, queryset)

    def process_node(self, node_id, students_queryset):
        node_data = self.graph[node_id]
        node_name = node_data['name']

        # Apply logic based on node type
        if node_name == 'filter_course':
            course_id = node_data['data'].get('course_id')
            if course_id:
                students_queryset = students_queryset.filter(course_id=course_id)
        
        elif node_name == 'filter_semester':
            semester_id = node_data['data'].get('semester_id')
            if semester_id:
                students_queryset = students_queryset.filter(semester=semester_id)

        elif node_name == 'filter_marks':
            # Simplified marks filter: total marks in some subject < threshold
            # In a real system, this would be more specific.
            min_marks = node_data['data'].get('min_marks', 0)
            max_marks = node_data['data'].get('max_marks', 100)
            # This is a bit complex to filter directly on queryset without context, 
            # but for demonstration we'll filter students who have any result in this range.
            students_queryset = students_queryset.filter(studentresult__total__gte=min_marks, studentresult__total__lte=max_marks).distinct()

        elif node_name == 'action_email':
            template_id = node_data['data'].get('template_id')
            if template_id:
                self.execute_email_action(template_id, students_queryset)
        
        elif node_name == 'action_log':
            message = node_data['data'].get('message', 'Workflow action executed')
            self.execute_log_action(message, students_queryset)

        # Traverse to next connected nodes
        outputs = node_data.get('outputs', {})
        for output_key, output_data in outputs.items():
            for connection in output_data.get('connections', []):
                next_node_id = connection['node']
                # Sub-branching: pass the filtered queryset to the next node
                self.process_node(next_node_id, students_queryset)

    def execute_email_action(self, template_id, students_queryset):
        try:
            template = EmailTemplate.objects.get(id=template_id)
            for student in students_queryset:
                # Prepare dynamic variables
                context = {
                    'student_name': student.admin.get_full_name(),
                    'department': student.course.name if student.course else 'N/A',
                    'semester': student.get_semester_display(),
                    'attendance_percentage': self.calculate_attendance(student),
                    # Add more variables as needed
                }
                
                # Render subject and body
                subject_tpl = Template(template.subject)
                body_tpl = Template(template.body)
                
                rendered_subject = subject_tpl.render(Context(context))
                rendered_body = body_tpl.render(Context(context))

                # Send Email
                send_mail(
                    rendered_subject,
                    "", # Message body (plain text)
                    settings.EMAIL_HOST_USER,
                    [student.admin.email],
                    fail_silently=True,
                    html_message=rendered_body
                )

                # Log execution
                WorkflowExecutionLog.objects.create(
                    workflow=self.workflow,
                    student=student,
                    status='success',
                    log_message=f"Sent email: {rendered_subject}"
                )
        except Exception as e:
            WorkflowExecutionLog.objects.create(
                workflow=self.workflow,
                status='error',
                log_message=f"Email Action Error: {str(e)}"
            )

    def execute_log_action(self, message, students_queryset):
        for student in students_queryset:
            WorkflowExecutionLog.objects.create(
                workflow=self.workflow,
                student=student,
                status='success',
                log_message=f"Activity Log: {message}"
            )

    def calculate_attendance(self, student):
        # Implementation of attendance calculation
        total = AttendanceReport.objects.filter(student=student).count()
        if total == 0: return 0
        present = AttendanceReport.objects.filter(student=student, status=True).count()
        return round((present / total) * 100, 2)
