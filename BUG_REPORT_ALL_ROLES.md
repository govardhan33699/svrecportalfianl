# COMPREHENSIVE BUG REPORT - ALL ROLES (HOD, STAFF, STUDENT)

## CRITICAL BUGS FOUND

---

## 🔴 BUG #1: USER_TYPE INCONSISTENT COMPARISON (STRING VS INTEGER)
**Severity:** CRITICAL - Data Type Mismatch  
**Location:** Multiple files

### Issue:
- `user_type` field stored as CharField (STRING): `max_length=1`
- **signals.py (models.py)** uses INTEGER comparison: `if instance.user_type == 1:`
- **middleware.py** uses STRING comparison: `if user.user_type == '1':`
- **views.py** uses STRING comparison: `if user.user_type == '1':`

### Problem:
```python
# In models.py (WRONG - Integer comparison for string field)
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:  # ❌ BUG: Comparing string to int
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:  # ❌ BUG
            Staff.objects.create(admin=instance)
        if instance.user_type == 3:  # ❌ BUG
            Student.objects.create(admin=instance)

# In middleware.py (CORRECT but INCONSISTENT)
if user.user_type == '1':  # ✅ String comparison
    return redirect(reverse('admin_home'))
```

### Impact:
- **Signal handlers may NOT trigger properly** when users are created
- Admin/Staff/Student profiles may NOT be auto-created
- Leads to users created but profile objects missing

### Fix:
Make all comparisons consistent using STRING (since field is CharField):
```python
if instance.user_type == '1':  # Use string, not integer
if instance.user_type == '2':
if instance.user_type == '3':
```

---

## 🔴 BUG #2: MISSING PERMISSION CHECKS IN HOD VIEWS
**Severity:** HIGH - Access Control Vulnerability  
**Location:** `hod_views.py`

### Issue:
View functions accept ANY user without validating they are HOD/Admin

### Affected Functions:
```python
def add_student(request):  # ❌ NO check if user is HOD
def add_staff(request):    # ❌ NO check if user is HOD
def add_course(request):   # ❌ NO check if user is HOD
def add_subject(request):  # ❌ NO check if user is HOD
def manage_staff(request): # ❌ NO check if user is HOD
def manage_student(request): # ❌ NO check if user is HOD
def edit_staff(request, staff_id): # ❌ NO check if user is HOD
def edit_student(request, student_id): # ❌ NO check if user is HOD
def delete_staff(request, staff_id): # ❌ NO check if user is HOD
def delete_student(request, student_id): # ❌ NO check if user is HOD
```

### Example Vulnerability:
```python
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    # ❌ NO CHECK: Any authenticated user can delete any student!
    user.delete()
    return redirect(reverse('manage_student'))
```

### Impact:
- **Staff members can DELETE students** by directly accessing URLs
- **Students can DELETE other students** by guessing URLs
- No role-based access control

### Fix:
Add permission decorators or checks:
```python
def delete_student(request, student_id):
    if request.user.user_type != '1':  # Only HOD (type 1)
        messages.error(request, "Unauthorized access")
        return redirect(reverse('admin_home'))
    # ... rest of code
```

---

## 🔴 BUG #3: MISSING CSRF PROTECTION + NO ROLE CHECK
**Severity:** HIGH - Security Vulnerability  
**Location:** `hod_views.py` - Multiple CSRF-exempt endpoints

### Issue:
CSRF_exempt endpoints don't verify user role:

```python
@csrf_exempt
def send_student_notification(request):
    # ❌ NO user_type check - ANY user can send notifications
    id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(Student, admin_id=id)
    # ... sends notification
    
@csrf_exempt
def view_student_leave(request):
    # ❌ NO user_type check - ANY user can approve/deny leaves
    leave.status = request.POST.get('status')
    leave.save()
```

### Affected Functions:
- `send_student_notification` - Any user can spam notifications
- `send_staff_notification` - Any user can spam notifications
- `view_student_leave` - Any user can approve leaves
- `view_staff_leave` - Any user can approve leaves
- `student_feedback_message` - Any user can reply to feedback
- `staff_feedback_message` - Any user can reply to feedback

### Impact:
**Students/Staff can impersonate HOD by accessing CSRF-exempt endpoints**

### Fix:
```python
@csrf_exempt
def send_student_notification(request):
    if request.user.user_type != '1':  # ❌ ADD THIS
        return redirect(reverse('login_page'))
    # ... rest of code
```

---

## 🟡 BUG #4: STAFF VIEWS INCORRECT ROLE CHECK
**Severity:** MEDIUM - Logic Error  
**Location:** `staff_views.py` line 511

### Issue:
```python
def staff_add_result(request):
    if request.user.user_type == '1':  # ❌ WRONG
        subjects = Subject.objects.all()
    else:
        staff = get_object_or_404(Staff, admin=request.user)
        subjects = Subject.objects.filter(staff=staff)
```

**Problem:** Type '1' is HOD, not STAFF!  
Type '2' is STAFF.

### Impact:
- HOD sees all subjects (correct by accident)
- Staff members get filtered correctly (but wrong condition logic)
- Code is confusing and error-prone

### Fix:
```python
def staff_add_result(request):
    if request.user.user_type == '2':  # Check if STAFF specifically
        staff = get_object_or_404(Staff, admin=request.user)
        subjects = Subject.objects.filter(staff=staff)
    else:
        subjects = Subject.objects.all()  # HOD or default
```

---

## 🟡 BUG #5: TYPE CASTING CONFUSION - INTEGER VS STRING
**Severity:** MEDIUM - Data Type Inconsistency  
**Location:** `add_staff`, `add_student` in hod_views.py

### Issue:
```python
# In add_student():
user = CustomUser.objects.create_user(
    email=email, 
    password=password, 
    user_type=3,  # ❌ PASSING INTEGER
    ...
)

# user_type field is CharField(max_length=1)
# Stored as STRING '3' but passed as INTEGER 3
```

### Impact:
- Django auto-converts but inconsistent with middleware/views
- Increases bugs when string comparisons fail
- Database stores as string '3', signals check integer 3

### Fix:
```python
user = CustomUser.objects.create_user(
    email=email,
    password=password,
    user_type='3',  # ✅ PASS AS STRING
    ...
)
```

---

## 🟡 BUG #6: EXCEPTION HANDLING TOO BROAD
**Severity:** MEDIUM - Error Handling Issue  
**Location:** Multiple view functions

### Issue:
```python
def delete_student(request, student_id):
    try:
        # ... delete code
    except Exception as e:  # ❌ TOO BROAD
        messages.error(request, "Error: " + str(e))
```

### Problems:
- Catches ALL exceptions (KeyError, TypeError, IntegrityError, etc.)
- Hides real errors
- Hard to debug
- May catch unrelated exceptions

### Impact:
- Legitimate errors hidden
- Security issues masked
- Difficult to maintain

### Fix:
```python
try:
    # ... delete code
except Student.DoesNotExist:  # ✅ SPECIFIC
    messages.error(request, "Student not found")
except ProtectedError:  # ✅ SPECIFIC
    messages.error(request, "Cannot delete - related records exist")
except Exception as e:  # ✅ FALLBACK ONLY
    logger.exception("Unexpected error")
    messages.error(request, "An unexpected error occurred")
```

---

## 🟡 BUG #7: MISSING USER AUTHENTICATION CHECKS
**Severity:** MEDIUM - Access Control  
**Location:** All student/staff/hod view endpoints

### Issue:
Many view functions don't verify the current user:

```python
def student_home(request):
    # ❌ Should verify: request.user.user_type == '3'
    # What if Staff member accesses this?
    
def staff_home(request):
    # ❌ Should verify: request.user.user_type == '2'
    # What if HOD member accesses this?
```

### Impact:
- Middleware provides some protection
- But direct URL hammering + session hijacking could bypass
- Views should have explicit role checks as fail-safe

### Fix:
```python
def student_home(request):
    if request.user.user_type != '3':
        messages.error(request, "Access denied")
        return redirect(reverse('login_page'))
    # ... rest of code
```

---

## 🟡 BUG #8: FILE UPLOAD SECURITY ISSUE
**Severity:** MEDIUM - Security Risk  
**Location:** `add_staff`, `add_student` - File handling

### Issue:
```python
passport = request.FILES.get('profile_pic')
fs = FileSystemStorage()
filename = fs.save(passport.name, passport)  # ❌ DANGEROUS
passport_url = fs.url(filename)
```

### Problems:
- No file type validation (could upload executable)
- No file size check (DoS attack)
- User filename used directly (path traversal possible)
- No virus/malware scan

### Impact:
- Arbitrary file uploads possible
- Server space exhaustion (DoS)
- Code execution risk

### Fix:
```python
import os
from django.core.exceptions import ValidationError

def validate_profile_pic(file):
    allowed_ext = ['.jpg', '.jpeg', '.png', '.gif']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_ext:
        raise ValidationError("Only image files allowed")
    if file.size > 5 * 1024 * 1024:  # 5MB limit
        raise ValidationError("File too large")
```

---

## 🟡 BUG #9: INCONSISTENT ERROR RESPONSES
**Severity:** LOW - Poor Error Handling  
**Location:** Multiple ajax endpoints

### Issue:
```python
# Inconsistent return types
return HttpResponse(True)   # String 'True'
return HttpResponse(False)  # String 'False'
return JsonResponse({'status': 'ok'})  # JSON
return False  # Boolean (wrong)
```

### Impact:
- Frontend can't parse responses consistently
- JavaScript receives string "False" instead of false
- Leads to bugs in error handling

### Fix:
Use consistent JSON responses:
```python
return JsonResponse({'status': 'success'})
return JsonResponse({'status': 'error', 'message': 'Details'})
```

---

## 🟡 BUG #10: SQL INJECTION RISK IN QUERIES
**Severity:** LOW (Django ORM provides protection)  
**Location:** Direct string queries (if any)

### Issue:
Most queries use ORM (safe), but some directly construct:
```python
# Generally safe with Django ORM, but watch for filter() with raw inputs
students = students.filter(student__roll_number__icontains=enrollment_number)
# ✅ Safe - ORM parameterizes
```

### Status:
- Currently passes parameterized queries ✅
- No SQL injection vulnerabilities detected

---

## 📊 SUMMARY OF BUGS BY IMPACT

| Priority | Count | Issues |
|----------|-------|--------|
| 🔴 CRITICAL | 2 | Type mismatch (string/int), Missing permission checks |
| 🟡 MEDIUM | 5 | CSRF gaps, Role check bugs, Broad exceptions, Auth gaps, File uploads |
| 🟢 LOW | 3 | Error response format, Logging gaps |

---

## ✅ RECOMMENDATIONS (Priority Order)

### 1. **IMMEDIATE** (Next 24 hours)
- Fix signal handlers: Change all `== 1` to `== '1'` in models.py
- Add role checks to all HOD views (user_type != '1' check)
- Add role checks to CSRF-exempt endpoints

### 2. **SHORT TERM** (This week)
- Add explicit role validation to staff_views functions
- Implement proper exception handling (catch specific exceptions)
- Add file upload validation

### 3. **MEDIUM TERM** (This month)
- Create a @role_required decorator for cleaner code
- Standardize response format (always use JSON)
- Add request logging for security audit trail
- Implement CSRF token validation

### 4. **LONG TERM** (Next sprint)
- Add unit tests for role-based access control
- Security audit of all endpoints
- Add input validation middleware
- Implement rate limiting

---

## CODE FIX TEMPLATE

Create `main_app/decorators.py`:
```python
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

def role_required(required_role):
    """Decorator to check user role"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(reverse('login_page'))
            if str(request.user.user_type) != str(required_role):
                messages.error(request, "Unauthorized access")
                return redirect(reverse('admin_home'))
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage:
# @role_required('1')  # Only HOD
# def add_student(request):
#     ...
```

---

**Generated:** April 11, 2026  
**Report Type:** Comprehensive Security & Bug Audit  
**Scope:** All user roles (HOD=1, Staff=2, Student=3)
