from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from .models import Subject, Staff, Student, StudentResult
from .forms import EditResultForm
from django.urls import reverse


class EditResultView(View):
    def get(self, request, *args, **kwargs):
        resultForm = EditResultForm()
        staff = get_object_or_404(Staff, admin=request.user)
        resultForm.fields['subject'].queryset = Subject.objects.filter(staff=staff)
        context = {
            'form': resultForm,
            'page_title': "Edit Student's Marks"
        }
        return render(request, "staff_template/edit_student_result.html", context)

    def post(self, request, *args, **kwargs):
        form = EditResultForm(request.POST)
        context = {'form': form, 'page_title': "Edit Student's Marks"}
        if form.is_valid():
            try:
                student = form.cleaned_data.get('student')
                subject = form.cleaned_data.get('subject')
                objective = form.cleaned_data.get('objective')
                descriptive = form.cleaned_data.get('descriptive')
                assignment = form.cleaned_data.get('assignment')
                total = form.cleaned_data.get('total')
                # Validating
                result = StudentResult.objects.get(student=student, subject=subject)
                result.objective = objective
                result.descriptive = descriptive
                result.assignment = assignment
                result.total = (objective / 2) + descriptive + assignment
                result.save()
                messages.success(request, "Marks Updated")
                return redirect(reverse('edit_student_result'))
            except Exception as e:
                messages.warning(request, "Marks Could Not Be Updated")
        else:
            messages.warning(request, "Marks Could Not Be Updated")
        return render(request, "staff_template/edit_student_result.html", context)
