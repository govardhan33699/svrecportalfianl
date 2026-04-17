"""
OPTIMIZATION SNIPPETS FOR STUDENT VIEWS
Copy these optimized view functions into student_views.py to replace existing ones
"""

# ============================================================================
# OPTIMIZED: student_view_announcement - With Pagination
# ============================================================================

def student_view_announcement_optimized(request):
    """Announcements with server-side pagination - Fast loading"""
    from django.db.models import Q
    today = date.today()
    
    page = request.GET.get('page', 1)
    
    announcements = Announcement.objects.filter(
        Q(audience__in=['all', 'student']) & 
        (Q(expires_at__isnull=True) | Q(expires_at__gte=today))
    ).select_related('created_by').defer('description_long').order_by('-created_at')
    
    # Apply pagination
    paginated = StudentPaginator.paginate_queryset(announcements, page=page, items_per_page=12)
    
    context = {
        'announcements': paginated['items'],
        'page': paginated['page'],
        'has_next': paginated['has_next'],
        'total_pages': paginated['total_pages'],
        'total_items': paginated['total_items'],
        'page_title': 'Announcements',
        'hide_sidebar': True,
    }
    return render(request, "student_template/student_view_announcement.html", context)


# ============================================================================
# OPTIMIZED: student_view_assignments - With Pagination & Query Optimization
# ============================================================================

def student_view_assignments_optimized(request):
    """Assignments with pagination and prefetch - Avoids N+1 queries"""
    student = get_object_or_404(Student, admin=request.user)
    page = request.GET.get('page', 1)
    
    # Optimized query: prefetch submissions for this student
    assignments_qs = Assignment.objects.filter(
        subject__course=student.course
    ).select_related('subject', 'subject__course').prefetch_related(
        Prefetch('assignmentsubmission_set', 
                queryset=AssignmentSubmission.objects.filter(student=student))
    ).defer('description_long', 'subject__description').order_by('-due_date')
    
    # Apply pagination
    paginated = StudentPaginator.paginate_queryset(assignments_qs, page=page, items_per_page=15)
    
    # Build submission map efficiently
    submission_map = {}
    for assignment in paginated['items']:
        subs = list(assignment.assignmentsubmission_set.all())
        submission_map[assignment.id] = subs[0] if subs else None
    
    context = {
        'assignments': paginated['items'],
        'submission_map': submission_map,
        'page': paginated['page'],
        'has_next': paginated['has_next'],
        'total_pages': paginated['total_pages'],
        'page_title': 'Assignments'
    }
    return render(request, "student_template/student_view_assignments.html", context)


# ============================================================================
# OPTIMIZED: student_view_material - With Pagination
# ============================================================================

def student_view_material_optimized(request):
    """Study materials with pagination and filtering"""
    student = get_object_or_404(Student, admin=request.user)
    page = request.GET.get('page', 1)
    subject_filter = request.GET.get('subject', None)
    
    materials_qs = StudyMaterial.objects.filter(
        subject__course=student.course
    ).select_related('subject', 'subject__course').defer('description_long')
    
    if subject_filter:
        materials_qs = materials_qs.filter(subject_id=subject_filter)
    
    materials_qs = materials_qs.order_by('-created_at')
    
    # Apply pagination
    paginated = StudentPaginator.paginate_queryset(materials_qs, page=page, items_per_page=15)
    
    # Get unique subjects for filter
    subjects = Subject.objects.filter(course=student.course).only('id', 'name')
    
    context = {
        'materials': paginated['items'],
        'subjects': subjects,
        'page': paginated['page'],
        'has_next': paginated['has_next'],
        'total_pages': paginated['total_pages'],
        'selected_subject': subject_filter,
        'page_title': 'Study Materials'
    }
    return render(request, "student_template/student_view_material.html", context)


# ============================================================================
# OPTIMIZED: student_cloud_storage - With Pagination & Categorization
# ============================================================================

def student_cloud_storage_optimized(request):
    """Cloud storage with pagination and lazy loading"""
    student = get_object_or_404(Student, admin=request.user)
    page = request.GET.get('page', 1)
    category_filter = request.GET.get('category', None)
    
    files_qs = StudentCloudFile.objects.filter(student=student).only(
        'id', 'student', 'file', 'category', 'created_at', 'file_size'
    )
    
    if category_filter:
        files_qs = files_qs.filter(category=category_filter)
    
    files_qs = files_qs.order_by('-created_at')
    
    # Apply pagination
    paginated = StudentPaginator.paginate_queryset(files_qs, page=page, items_per_page=20)
    
    context = {
        'files': paginated['items'],
        'page': paginated['page'],
        'has_next': paginated['has_next'],
        'total_pages': paginated['total_pages'],
        'selected_category': category_filter,
        'page_title': 'Cloud Storage'
    }
    
    # If AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        items_data = []
        for f in paginated['items']:
            items_data.append({
                'id': f.id,
                'name': f.file.name.split('/')[-1],
                'category': f.category,
                'size': f.file_size,
                'url': f.file.url,
            })
        return JsonResponse({
            'success': True,
            'items': items_data,
            'has_next': paginated['has_next'],
            'page': paginated['page'],
        })
    
    return render(request, "student_template/student_cloud_storage.html", context)


# ============================================================================
# OPTIMIZED: student_apply_leave - With Pagination of History
# ============================================================================

def student_apply_leave_optimized(request):
    """Leave application with paginated history"""
    form = LeaveReportStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    page = request.GET.get('page', 1)
    
    # Optimized leave history query
    leave_history_qs = LeaveReportStudent.objects.filter(
        student=student
    ).select_related('student', 'student__admin').defer('reason_long').order_by('-created_at')
    
    paginated = StudentPaginator.paginate_queryset(leave_history_qs, page=page, items_per_page=10)
    
    context = {
        'form': form,
        'leave_history': paginated['items'],
        'page': paginated['page'],
        'has_next': paginated['has_next'],
        'total_pages': paginated['total_pages'],
        'page_title': 'Apply for leave'
    }
    
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(request, "Application for leave has been submitted for review")
                return redirect(reverse('student_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Form has errors!")
    
    return render(request, "student_template/student_apply_leave.html", context)


# ============================================================================
# OPTIMIZED: student_feedback - With Paginated History
# ============================================================================

def student_feedback_optimized(request):
    """Feedback submission with paginated history"""
    form = FeedbackStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    page = request.GET.get('page', 1)
    
    # Optimized feedback query
    feedbacks_qs = FeedbackStudent.objects.filter(
        student=student
    ).only('id', 'student', 'subject', 'rating', 'message', 'created_at').order_by('-created_at')
    
    paginated = StudentPaginator.paginate_queryset(feedbacks_qs, page=page, items_per_page=10)
    
    context = {
        'form': form,
        'feedbacks': paginated['items'],
        'page': paginated['page'],
        'has_next': paginated['has_next'],
        'total_pages': paginated['total_pages'],
        'page_title': 'Student Feedback'
    }
    
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(request, "Feedback submitted for review")
                return redirect(reverse('student_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    
    return render(request, "student_template/student_feedback.html", context)


# ============================================================================
# AJAX ENDPOINTS FOR INFINITE SCROLL / LOAD MORE
# ============================================================================

def load_more_announcements(request):
    """AJAX endpoint for loading more announcements"""
    page = request.GET.get('page', 1)
    
    from django.db.models import Q
    today = date.today()
    
    announcements = Announcement.objects.filter(
        Q(audience__in=['all', 'student']) & 
        (Q(expires_at__isnull=True) | Q(expires_at__gte=today))
    ).select_related('created_by').defer('description_long').order_by('-created_at')
    
    return StudentPaginator.paginate_ajax(
        announcements, 
        page=int(page),
        serializer=lambda a: {
            'id': a.id,
            'title': a.title,
            'description': a.description[:200] + '...' if len(a.description) > 200 else a.description,
            'audience': a.audience,
            'created_at': a.created_at.strftime('%b %d, %Y'),
        }
    )


def load_more_assignments(request):
    """AJAX endpoint for loading more assignments"""
    student = get_object_or_404(Student, admin=request.user)
    page = request.GET.get('page', 1)
    
    assignments = Assignment.objects.filter(
        subject__course=student.course
    ).select_related('subject').defer('description_long').order_by('-due_date')
    
    return StudentPaginator.paginate_ajax(
        assignments,
        page=int(page),
        serializer=lambda a: {
            'id': a.id,
            'title': a.title,
            'subject': a.subject.name,
            'due_date': a.due_date.strftime('%b %d, %Y'),
            'max_marks': a.max_marks,
        }
    )


def load_more_materials(request):
    """AJAX endpoint for loading more materials"""
    student = get_object_or_404(Student, admin=request.user)
    page = request.GET.get('page', 1)
    
    materials = StudyMaterial.objects.filter(
        subject__course=student.course
    ).select_related('subject').defer('description_long').order_by('-created_at')
    
    return StudentPaginator.paginate_ajax(
        materials,
        page=int(page),
        serializer=lambda m: {
            'id': m.id,
            'title': m.title,
            'subject': m.subject.name,
            'created_at': m.created_at.strftime('%b %d, %Y'),
            'file_type': m.file_type if hasattr(m, 'file_type') else 'pdf',
        }
    )
