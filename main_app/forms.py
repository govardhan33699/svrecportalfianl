from django import forms
from django.forms.widgets import DateInput, TextInput, TimeInput
from django.forms import inlineformset_factory

from .models import *
from . import models


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Apply bootstrap text/select styling, but keep boolean widgets as checkboxes.
        for field in self.visible_fields():
            input_type = getattr(field.field.widget, 'input_type', None)
            if input_type in ('checkbox', 'radio'):
                field.field.widget.attrs['class'] = 'form-check-input'
                field.field.widget.attrs['style'] = (
                    'width:18px;height:18px;min-width:18px;display:inline-block;'
                    'appearance:auto;-webkit-appearance:checkbox;vertical-align:middle;'
                    'margin:0 8px 0 0;'
                )
            else:
                field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('', 'Select Gender'), ('M', 'Male'), ('F', 'Female')])
    full_name = forms.CharField(required=True, label='Name')
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        # Remove the model's first_name/last_name from rendered fields
        if 'first_name' in self.fields:
            del self.fields['first_name']
        if 'last_name' in self.fields:
            del self.fields['last_name']

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                if field in self.fields:
                    self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"
            # Combine first + last name into full_name
            fn = instance.get('first_name', '')
            ln = instance.get('last_name', '')
            self.fields['full_name'].initial = f"{fn} {ln}".strip()

        # Reorder fields to put full_name at the top
        field_order = list(self.fields.keys())
        if 'full_name' in field_order:
            field_order.remove('full_name')
            field_order.insert(0, 'full_name')
            self.order_fields(field_order)

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if not full_name:
            raise forms.ValidationError("Name is required")
        parts = full_name.rsplit(' ', 1)
        if len(parts) == 2:
            self.cleaned_data['first_name'] = parts[0]
            self.cleaned_data['last_name'] = parts[1]
        else:
            self.cleaned_data['first_name'] = parts[0]
            self.cleaned_data['last_name'] = ''
        return full_name

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['email', 'gender', 'password', 'profile_pic', 'address']


class StudentForm(CustomUserForm):
    academic_year = forms.ModelChoiceField(queryset=AcademicLevel.objects.all(), empty_label="Select Year", required=False)
    semester = forms.ModelChoiceField(queryset=AcademicSemester.objects.all(), empty_label="Select Semester", required=False)

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields['course'].empty_label = "Select Course"
        self.fields['session'].empty_label = "Select Academic Year"

        self.fields['regulation'].empty_label = "Select Regulation"
        
        # Add blank choices to ChoiceFields
        self.fields['section'].choices = [('', 'Select Section')] + list(self.fields['section'].choices)
        self.fields['blood_group'].choices = [('', 'Select Blood Group')] + list(self.fields['blood_group'].choices)
        self.fields['admission_type'].choices = [('', 'Select Admission Type')] + list(self.fields['admission_type'].choices)
        
        # Remove pre-selections for ChoiceFields
        self.fields['section'].initial = ''

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + \
            ['course', 'session', 'regulation', 'roll_number', 'section', 'father_name', 'mother_name', 'mobile_number', 'parent_mobile_number', 'aadhar_number', 'caste', 'admission_number', 'academic_year', 'semester', 'blood_group', 'apaar_id', 'date_of_birth', 'annual_income', 'father_occupation', 'mother_occupation', 'mother_mobile_number', 'nationality', 'religion', 'mother_tongue', 'admission_date', 'admission_type']


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + \
            ['course', 'father_name', 'mother_name', 'aadhaar_number', 'pan_number', 'spouse_name', 'qualification', 'blood_group', 'designation', 'faculty_role', 'date_of_birth', 'date_of_joining', 'experience', 'mobile_number']
        widgets = {
            'date_of_birth': DateInput(attrs={'type': 'date'}),
            'date_of_joining': DateInput(attrs={'type': 'date'}),
        }


class AcademicLevelForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(AcademicLevelForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']
        model = AcademicLevel


class AcademicSemesterForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(AcademicSemesterForm, self).__init__(*args, **kwargs)
        self.fields['academic_level'].empty_label = "Select Year"

    class Meta:
        fields = ['academic_level', 'name']
        model = AcademicSemester


class DegreeForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(DegreeForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']
        model = Degree


class CourseForm(FormSettings):
    degree = forms.ModelChoiceField(queryset=Degree.objects.all(), empty_label="Select Course", required=True)
    
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['degree', 'name']
        model = Course


class SubjectForm(FormSettings):
    name = forms.CharField(label="Subject Name", max_length=120)
    code = forms.CharField(label="Subject Code", max_length=20, required=False)
    short_code = forms.CharField(label="Short Code", max_length=10, required=False)
    
    # Add checkboxes for tracking options
    show_in_attendance = forms.BooleanField(
        label="Include in Attendance Tracking",
        required=False,
        help_text="Enable attendance recording for this subject"
    )
    show_in_results = forms.BooleanField(
        label="Include in Results",
        required=False,
        help_text="Show grades and results for this subject"
    )
    show_in_marks = forms.BooleanField(
        label="Include in Marks Memo",
        required=False,
        help_text="Display in student marks memorandum"
    )

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Subject
        fields = ['name', 'code', 'short_code', 'staff', 'course', 'regulation', 
                  'semester', 'credits', 'show_in_attendance', 'show_in_results', 'show_in_marks']


class SessionForm(FormSettings):
    start_year = forms.IntegerField(label="Start Year", min_value=1900, max_value=2100)
    end_year = forms.IntegerField(label="End Year", min_value=1900, max_value=2100)

    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.start_year:
                try:
                    self.fields['start_year'].initial = self.instance.start_year.year
                except AttributeError:
                    pass
            if self.instance.end_year:
                try:
                    self.fields['end_year'].initial = self.instance.end_year.year
                except AttributeError:
                    pass

    def clean_start_year(self):
        year = self.cleaned_data.get('start_year')
        from datetime import date
        return date(year, 1, 1)

    def clean_end_year(self):
        year = self.cleaned_data.get('end_year')
        from datetime import date
        return date(year, 1, 1)

    class Meta:
        model = Session
        fields = ['start_year', 'end_year']



class RegulationForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(RegulationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Regulation
        fields = ['name', 'course', 'session']



class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStaffForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']


class LeaveReportStudentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStudentForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStudent
        fields = ['feedback']


class StudentEditForm(CustomUserForm):
    academic_year = forms.ModelChoiceField(queryset=AcademicLevel.objects.all(), empty_label="Select Year", required=False)
    semester = forms.ModelChoiceField(queryset=AcademicSemester.objects.all(), empty_label="Select Semester", required=False)

    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + \
            ['course', 'session', 'regulation', 'roll_number', 'section', 'father_name', 'mother_name', 'mobile_number', 'parent_mobile_number', 'aadhar_number', 'caste', 'admission_number', 'academic_year', 'semester', 'blood_group', 'apaar_id', 'date_of_birth', 'annual_income', 'father_occupation', 'mother_occupation', 'mother_mobile_number', 'nationality', 'religion', 'mother_tongue', 'admission_date', 'admission_type']


class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + \
            ['course', 'father_name', 'mother_name', 'aadhaar_number', 'pan_number', 'spouse_name', 'qualification', 'blood_group', 'designation', 'faculty_role', 'date_of_birth', 'date_of_joining', 'experience', 'mobile_number']
        widgets = {
            'date_of_birth': DateInput(attrs={'type': 'date'}),
            'date_of_joining': DateInput(attrs={'type': 'date'}),
        }


StaffQualificationFormSet = inlineformset_factory(
    Staff,
    StaffQualification,
    fields=('examination_passed', 'classification', 'percentage_of_marks', 'year', 'university_institution'),
    extra=1,
    can_delete=True
)


class EditResultForm(FormSettings):
    session_list = Session.objects.all()
    session_year = forms.ModelChoiceField(
        label="Session Year", queryset=session_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)
        self.fields['objective'].widget.attrs.update({'max': '10', 'min': '0'})
        self.fields['descriptive'].widget.attrs.update({'max': '30', 'min': '0'})
        self.fields['assignment'].widget.attrs.update({'max': '5', 'min': '0'})

    def clean_objective(self):
        objective = self.cleaned_data.get('objective')
        if objective > 10:
            raise forms.ValidationError("Objective marks cannot exceed 10")
        return objective

    def clean_descriptive(self):
        descriptive = self.cleaned_data.get('descriptive')
        if descriptive > 30:
            raise forms.ValidationError("Descriptive marks cannot exceed 30")
        return descriptive

    def clean_assignment(self):
        assignment = self.cleaned_data.get('assignment')
        if assignment > 5:
            raise forms.ValidationError("Assignment marks cannot exceed 5")
        return assignment

    class Meta:
        model = StudentResult
        fields = ['session_year', 'subject', 'student', 'objective', 'descriptive', 'assignment', 'total']

#todos
# class TodoForm(forms.ModelForm):
#     class Meta:
#         model=Todo
#         fields=["title","is_finished"]

#issue book

class IssueBookForm(forms.Form):
    isbn2 = forms.ModelChoiceField(queryset=models.Book.objects.all(), empty_label="Book Name [ISBN]", to_field_name="isbn", label="Book (Name and ISBN)")
    name2 = forms.ModelChoiceField(queryset=models.Student.objects.all(), empty_label="Name ", to_field_name="", label="Student Details")
    
    isbn2.widget.attrs.update({'class': 'form-control'})
    name2.widget.attrs.update({'class':'form-control'})


class PeriodForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(PeriodForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Period
        fields = ['number', 'start_time', 'end_time']
        widgets = {
            'start_time': TimeInput(attrs={'type': 'time'}),
            'end_time': TimeInput(attrs={'type': 'time'}),
        }


class TimetableForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(TimetableForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Timetable
        fields = ['course', 'section', 'semester', 'subject', 'day', 'period', 'staff']


class AssignmentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Assignment
        fields = ['subject', 'title', 'description', 'due_date', 'file']
        widgets = {
            'due_date': DateInput(attrs={'type': 'date'}),
        }


class AssignmentSubmissionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(AssignmentSubmissionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.AssignmentSubmission
        fields = ['file']


class StudentChangePasswordForm(forms.Form):
    email = forms.EmailField(label="Email (Username)", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}))
    
    new_password = forms.CharField(required=False, label="New Password (optional)", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password to change'}))
    confirm_password = forms.CharField(required=False, label="Confirm Password", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}))

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class StaffTimetableForm(FormSettings):
    def __init__(self, *args, **kwargs):
        staff_id = kwargs.pop('staff_id', None)
        super(StaffTimetableForm, self).__init__(*args, **kwargs)
        if staff_id:
            self.fields['subject'].queryset = models.Subject.objects.filter(staff__admin_id=staff_id)
            course_ids = models.Subject.objects.filter(staff__admin_id=staff_id).values_list('course_id', flat=True).distinct()
            self.fields['course'].queryset = models.Course.objects.filter(id__in=course_ids)

    class Meta:
        model = models.Timetable
        fields = ['course', 'section', 'subject', 'day', 'period']


class AnnouncementForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(AnnouncementForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Announcement
        fields = ['title', 'content', 'category', 'audience', 'expires_at']
        widgets = {
            'expires_at': DateInput(attrs={'type': 'date'}),
        }


class AcademicCalendarForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(AcademicCalendarForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AcademicCalendar
        fields = ['session', 'semester', 'regulation', 'commencement_date', 'instruction_end_date']
        widgets = {
            'commencement_date': DateInput(attrs={'type': 'date'}),
            'instruction_end_date': DateInput(attrs={'type': 'date'}),
        }


class CalendarEventForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(CalendarEventForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.CalendarEvent
        fields = ['event_type', 'custom_name', 'start_date', 'end_date', 'duration_text', 'order']
        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
            'order': TextInput(attrs={'type': 'number', 'min': '0'}),
        }


CalendarEventFormSet = inlineformset_factory(
    AcademicCalendar,
    models.CalendarEvent,
    form=CalendarEventForm,
    fields=['event_type', 'custom_name', 'start_date', 'end_date', 'duration_text', 'order'],
    extra=1,
    can_delete=True,
    widgets={
        'start_date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        'end_date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        'order': TextInput(attrs={'type': 'number', 'min': '0', 'class': 'form-control'}),
    }
)

class StudentCertificateForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(StudentCertificateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentCertificate
        fields = ['title', 'certificate_type', 'issued_by', 'issue_date', 'file', 'description']
        widgets = {
            'issue_date': DateInput(attrs={'type': 'date'}),
        }

class EmailTemplateForm(FormSettings):
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 10, 'class': 'form-control', 'id': 'email_body'}),
        }
