from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Announcement, StudentResult, Assignment, Workflow, Student
from .workflow_engine import WorkflowEngine

@receiver(post_save, sender=Announcement)
def trigger_announcement_workflow(sender, instance, created, **kwargs):
    if created:
        # Find all active workflows for announcements
        workflows = Workflow.objects.filter(trigger_type='announcement', is_active=True)
        for workflow in workflows:
            engine = WorkflowEngine(workflow.id)
            # Find relevant students based on audience
            if instance.audience == 'all' or instance.audience == 'student':
                engine.run() # Run for all students (or filtered by graph)

@receiver(post_save, sender=StudentResult)
def trigger_marks_workflow(sender, instance, created, **kwargs):
    if created:
        workflows = Workflow.objects.filter(trigger_type='marks', is_active=True)
        for workflow in workflows:
            engine = WorkflowEngine(workflow.id)
            # Run specifically for this student
            engine.run(student_ids=[instance.student.id])

@receiver(post_save, sender=Assignment)
def trigger_assignment_workflow(sender, instance, created, **kwargs):
    if created:
        workflows = Workflow.objects.filter(trigger_type='assignment', is_active=True)
        for workflow in workflows:
            engine = WorkflowEngine(workflow.id)
            # Find students in the course/semester of the subject
            students = Student.objects.filter(course=instance.subject.course, semester=instance.subject.semester)
            engine.run(student_ids=[s.id for s in students])
