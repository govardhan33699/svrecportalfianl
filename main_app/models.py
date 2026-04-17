from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime,timedelta


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return f"{self.start_year.year} - {self.end_year.year}"



class Degree(models.Model):
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AcademicLevel(models.Model):
    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AcademicSemester(models.Model):
    name = models.CharField(max_length=20)
    academic_level = models.ForeignKey(AcademicLevel, on_delete=models.CASCADE, related_name='semesters')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.academic_level.name})"


class Course(models.Model):
    name = models.CharField(max_length=120)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    USER_TYPE = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    GENDER = [("M", "Male"), ("F", "Female")]
    
    
    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField()
    address = models.TextField()
    fcm_token = models.TextField(default="")  # For firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return  self.first_name + " " + self.last_name


SEMESTER_CHOICES = [
    ('1', '1-1'), ('2', '1-2'), ('3', '2-1'),
    ('4', '2-2'), ('5', '3-1'), ('6', '3-2'),
    ('7', '4-1'), ('8', '4-2'),
]


class Regulation(models.Model):
    name = models.CharField(max_length=120)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Academic Year")


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)



    def __str__(self):
        return self.name

class Book(models.Model):
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.PositiveIntegerField()
    category = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name) + " ["+str(self.isbn)+']'


class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True, verbose_name="Academic Year")

    regulation = models.ForeignKey(Regulation, on_delete=models.DO_NOTHING, null=True, blank=True)
    SECTION = [("A", "Section A"), ("B", "Section B"), ("C", "Section C")]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    ADMISSION_TYPE_CHOICES = [
        ('management', 'Management'),
        ('convenor', 'Convenor'),
    ]
    roll_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    section = models.CharField(max_length=1, choices=SECTION, default='A')
    father_name = models.CharField(max_length=150, null=True, blank=True)
    mother_name = models.CharField(max_length=150, null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    parent_mobile_number = models.CharField(max_length=15, null=True, blank=True)
    aadhar_number = models.CharField(max_length=12, null=True, blank=True)
    caste = models.CharField(max_length=50, null=True, blank=True)
    # New fields
    admission_number = models.CharField(max_length=50, null=True, blank=True)
    academic_year = models.ForeignKey(AcademicLevel, on_delete=models.SET_NULL, null=True, blank=True)
    semester = models.ForeignKey(AcademicSemester, on_delete=models.SET_NULL, null=True, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)
    apaar_id = models.CharField(max_length=50, null=True, blank=True)
    # Additional detail fields
    date_of_birth = models.DateField(null=True, blank=True)
    annual_income = models.CharField(max_length=20, null=True, blank=True)
    father_occupation = models.CharField(max_length=100, null=True, blank=True)
    mother_occupation = models.CharField(max_length=100, null=True, blank=True)
    mother_mobile_number = models.CharField(max_length=15, null=True, blank=True)
    nationality = models.CharField(max_length=50, default='Indian', null=True, blank=True)
    religion = models.CharField(max_length=50, null=True, blank=True)
    mother_tongue = models.CharField(max_length=50, null=True, blank=True)
    admission_date = models.DateField(null=True, blank=True)
    admission_type = models.CharField(max_length=20, choices=ADMISSION_TYPE_CHOICES, null=True, blank=True)
    
    # Contact Details
    landline = models.CharField(max_length=15, null=True, blank=True, verbose_name="LandLine")
    parent_email = models.EmailField(null=True, blank=True, verbose_name="Parent Email")
    
    # Address Details
    door_no = models.CharField(max_length=50, null=True, blank=True, verbose_name="Door No")
    street = models.CharField(max_length=200, null=True, blank=True)
    area_village = models.CharField(max_length=100, null=True, blank=True, verbose_name="Area (Village)")
    mandal = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True, verbose_name="PinCode")

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name

class Library(models.Model):
    student = models.ForeignKey(Student,  on_delete=models.CASCADE, null=True, blank=False)
    book = models.ForeignKey(Book,  on_delete=models.CASCADE, null=True, blank=False)
    def __str__(self):
        return str(self.student)

def expiry():
    return datetime.today() + timedelta(days=14)
class IssuedBook(models.Model):
    student_id = models.CharField(max_length=100, blank=True) 
    isbn = models.CharField(max_length=13)
    issued_date = models.DateField(auto_now=True)
    expiry_date = models.DateField(default=expiry)



class Staff(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    FACULTY_ROLE_CHOICES = [
        ('class_teacher', 'Class Teacher'),
        ('subject_teacher', 'Subject Teacher'),
    ]
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    staff_code = models.CharField(max_length=20, null=True, blank=True)
    # New fields
    father_name = models.CharField(max_length=150, null=True, blank=True)
    mother_name = models.CharField(max_length=150, null=True, blank=True)
    aadhaar_number = models.CharField(max_length=12, null=True, blank=True)
    pan_number = models.CharField(max_length=10, null=True, blank=True)
    spouse_name = models.CharField(max_length=150, null=True, blank=True)
    qualification = models.CharField(max_length=200, null=True, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    faculty_role = models.CharField(max_length=20, choices=FACULTY_ROLE_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    experience = models.CharField(max_length=50, null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.admin.first_name + " " +  self.admin.last_name


class StaffQualification(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='qualifications')
    examination_passed = models.CharField(max_length=200)
    classification = models.CharField(max_length=100, null=True, blank=True)
    percentage_of_marks = models.CharField(max_length=20, null=True, blank=True)
    year = models.CharField(max_length=20, null=True, blank=True)
    university_institution = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.examination_passed} - {self.staff.admin.first_name}"


class Subject(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, null=True, blank=True)
    short_code = models.CharField(max_length=10, null=True, blank=True)
    max_marks = models.PositiveIntegerField(default=30)
    show_in_attendance = models.BooleanField(default=True, help_text="Track attendance for this subject")
    show_in_results = models.BooleanField(default=True, help_text="Show results/grades for this subject")
    show_in_marks = models.BooleanField(default=True, help_text="Show in marks memo")
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    regulation = models.ForeignKey(Regulation, on_delete=models.SET_NULL, null=True, blank=True)
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, null=True, blank=True)
    credits = models.FloatField(default=0)
    order = models.PositiveIntegerField(default=1, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name="Academic Year")

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    period = models.ForeignKey('Period', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, null=True, blank=True)
    exam_name = models.CharField(max_length=50, null=True, blank=True)
    objective = models.FloatField(default=0)
    descriptive = models.FloatField(default=0)
    assignment = models.FloatField(default=0)
    internal_marks = models.FloatField(default=0)
    external_marks = models.FloatField(default=0)
    total = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Period(models.Model):
    number = models.PositiveIntegerField(unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Period {self.number} ({self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')})"


class Timetable(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section = models.CharField(max_length=1, choices=[("A", "Section A"), ("B", "Section B"), ("C", "Section C")], default='A')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, null=True, blank=True)

    class Meta:
        ordering = ['day', 'period__number']
        unique_together = ['course', 'section', 'day', 'period', 'semester']

    def __str__(self):
        return f"{self.day} - Period {self.period.number} - {self.subject.name}"


class Assignment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.subject.name}"


class AssignmentSubmission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='assignment_submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')
    marks = models.FloatField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student} - {self.assignment.title}"


class StudyMaterial(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    file = models.FileField(upload_to='study_materials/')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.subject.name}"


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    CATEGORY_CHOICES = [
        ('news', 'News'),
        ('mid', 'Mid Exams'),
        ('sem', 'Semester Exams'),
        ('placement', 'Placements'),
        ('holiday', 'Holidays'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    audience = models.CharField(max_length=20, choices=[('all', 'All'), ('staff', 'Staff'), ('student', 'Student')], default='all')
    expires_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class AcademicCalendar(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name="Academic Year")

    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES)
    regulation = models.ForeignKey(Regulation, on_delete=models.CASCADE, null=True, blank=True)
    commencement_date = models.DateField(null=True, blank=True)
    instruction_end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['session', 'semester', 'regulation']

    def __str__(self):
        return f"{self.session} - {self.get_semester_display()}"

    @property
    def instruction_duration_text(self):
        if self.commencement_date and self.instruction_end_date:
            delta = self.instruction_end_date - self.commencement_date
            weeks = round(delta.days / 7)
            return f"{weeks} Weeks"
        return "—"


class CalendarEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('mid1', 'I Mid-term Examinations'),
        ('mid2', 'II Mid-term Examinations'),
        ('lab_exam', 'Preparation & End Laboratory Examinations'),
        ('end_exam', 'End Theory Examinations'),
        ('workshop', 'Branch Specific Workshop'),
        ('results', 'Declaration of Results'),
        ('next_commencement', 'Commencement of Next Semester'),
        ('other', 'Other'),
    ]
    calendar = models.ForeignKey(AcademicCalendar, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    custom_name = models.CharField(max_length=200, blank=True, help_text='Used when event type is "Other"')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration_text = models.CharField(max_length=50, blank=True, help_text='e.g. "03 Days", "02 Weeks"')
    order = models.PositiveIntegerField(default=0, help_text='Display order')

    class Meta:
        ordering = ['order', 'start_date']

    def __str__(self):
        name = self.custom_name if self.event_type == 'other' else self.get_event_type_display()
        return f"{name} ({self.start_date})"

    @property
    def display_name(self):
        if self.event_type == 'other' and self.custom_name:
            return self.custom_name
        return self.get_event_type_display()

    @property
    def date_range_display(self):
        if not self.start_date:
            return "Not set"
        if self.end_date and self.end_date != self.start_date:
            return f"{self.start_date.strftime('%d-%m-%Y')} to {self.end_date.strftime('%d-%m-%Y')}"
        return self.start_date.strftime('%d-%m-%Y')


# ── Security Models ──

class FailedLoginAttempt(models.Model):
    """Tracks failed login attempts for rate limiting / brute-force protection."""
    email = models.EmailField(db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['email', 'attempted_at']),
            models.Index(fields=['ip_address', 'attempted_at']),
        ]

    def __str__(self):
        return f"Failed login for {self.email} at {self.attempted_at}"


class SecurityLog(models.Model):
    """Audit trail for authentication and security events."""
    EVENT_TYPES = [
        ('login_success', 'Login Success'),
        ('login_failed', 'Login Failed'),
        ('login_locked', 'Account Locked'),
        ('logout', 'Logout'),
        ('password_reset', 'Password Reset'),
        ('session_expired', 'Session Expired'),
    ]
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, db_index=True)
    email = models.EmailField(blank=True, default='')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    details = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.event_type} — {self.email} at {self.created_at}"


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if str(instance.user_type) == '1':  # ✅ FIX: Compare as strings
            Admin.objects.create(admin=instance)
        if str(instance.user_type) == '2':  # ✅ FIX: Compare as strings
            Staff.objects.create(admin=instance)
        if str(instance.user_type) == '3':  # ✅ FIX: Compare as strings
            Student.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if str(instance.user_type) == '1':  # ✅ FIX: Compare as strings
        instance.admin.save()
    if str(instance.user_type) == '2':  # ✅ FIX: Compare as strings
        instance.staff.save()
    if str(instance.user_type) == '3':  # ✅ FIX: Compare as strings
        instance.student.save()

class StudentCloudFile(models.Model):
    CATEGORY_CHOICES = [
        ('notes', 'Notes'),
        ('pdf', 'PDF'),
        ('question_paper', 'Question Paper'),
        ('important', 'Important File'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='student_cloud/')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='notes')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.student.admin.first_name}"

# Student Certificates
CERTIFICATE_TYPE_CHOICES = [
    ('Workshop', 'Workshop'),
    ('Sports', 'Sports'),
    ('Technical', 'Technical'),
    ('Others', 'Others'),
]

class StudentCertificate(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    certificate_type = models.CharField(max_length=50, choices=CERTIFICATE_TYPE_CHOICES)
    issued_by = models.CharField(max_length=200)
    issue_date = models.DateField()
    file = models.FileField(upload_to='student_certificates/')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.student.admin.first_name}"

# Workflow Automation System
class EmailTemplate(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=255)
    body = models.TextField()  # HTML content
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Workflow(models.Model):
    TRIGGER_CHOICES = [
        ('announcement', 'New Announcement'),
        ('marks', 'Marks Uploaded'),
        ('assignment', 'Assignment Created'),
        ('attendance', 'Attendance Alert'),
        ('manual', 'Manual Trigger'),
    ]
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    graph_data = models.JSONField()  # Drawflow JSON data
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class WorkflowExecutionLog(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('error', 'Error'),
    ]
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    log_message = models.TextField()
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.workflow.name} - {self.status} - {self.executed_at}"
