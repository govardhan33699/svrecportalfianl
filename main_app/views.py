import json
import requests
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .EmailBackend import EmailBackend
from .models import Attendance, Session, Subject, FailedLoginAttempt, SecurityLog


# ── Helper: get client IP ──
def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _get_user_agent(request):
    return request.META.get('HTTP_USER_AGENT', '')[:500]


def _log_security_event(event_type, email, request, user=None, details=''):
    """Create a SecurityLog entry."""
    SecurityLog.objects.create(
        event_type=event_type,
        email=email,
        user=user,
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
        details=details,
    )


def _is_login_locked(email, ip_address):
    """Check if login is locked due to too many failed attempts."""
    max_attempts = getattr(settings, 'LOGIN_MAX_ATTEMPTS', 5)
    lockout_seconds = getattr(settings, 'LOGIN_LOCKOUT_SECONDS', 900)
    cutoff = timezone.now() - timedelta(seconds=lockout_seconds)

    recent_failures = FailedLoginAttempt.objects.filter(
        email__iexact=email,
        attempted_at__gte=cutoff,
    ).count()

    return recent_failures >= max_attempts


def _record_failed_attempt(email, request):
    """Record a failed login attempt."""
    FailedLoginAttempt.objects.create(
        email=email,
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
    )


def _clear_failed_attempts(email):
    """Clear failed attempts after successful login."""
    FailedLoginAttempt.objects.filter(email__iexact=email).delete()


# ── Views ──

@never_cache
def login_page(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("admin_home"))
        elif request.user.user_type == '2':
            return redirect(reverse("staff_home"))
        else:
            return redirect(reverse("student_home"))
    return render(request, 'main_app/login.html')


@require_POST
def doLogin(request):
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')

    # ── Rate limiting: check if account is locked ──
    if _is_login_locked(email, _get_client_ip(request)):
        lockout_minutes = getattr(settings, 'LOGIN_LOCKOUT_SECONDS', 900) // 60
        _log_security_event('login_locked', email, request,
                            details=f'Account locked — too many failed attempts')
        messages.error(request, f"Too many failed attempts. Please try again after {lockout_minutes} minutes.")
        return redirect("/")

    # ── Authenticate ──
    user = EmailBackend.authenticate(request, username=email, password=password)

    if user is not None:
        # Capture previous login before Django's login() updates it
        previous_last_login = user.last_login

        # ── Session rotation: prevent session fixation ──
        request.session.cycle_key()

        login(request, user)

        # Store previous login in session
        if previous_last_login:
            request.session['previous_login'] = previous_last_login.strftime("%d %b %Y, %I:%M %p")

        # Handle "Remember Me"
        remember_me = request.POST.get('remember')
        if remember_me:
            request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
        else:
            request.session.set_expiry(0)  # Expire on browser close

        # ── Clear failed attempts & log success ──
        _clear_failed_attempts(email)
        _log_security_event('login_success', email, request, user=user)

        if user.user_type == '1':
            return redirect(reverse("admin_home"))
        elif user.user_type == '2':
            return redirect(reverse("staff_home"))

        else:
            return redirect(reverse("student_home"))
    else:
        # ── Record failure & log ──
        _record_failed_attempt(email, request)
        _log_security_event('login_failed', email, request,
                            details='Invalid credentials')

        # Generic error — never reveal whether email or password was wrong
        messages.error(request, "Invalid credentials")
        return redirect("/")


def logout_user(request):
    if request.user.is_authenticated:
        _log_security_event('logout', request.user.email, request, user=request.user)
    logout(request)
    return redirect("/")


@require_POST
def get_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = Attendance.objects.filter(subject=subject, session=session)
        attendance_list = []
        for attd in attendance:
            data = {
                    "id": attd.id,
                    "attendance_date": str(attd.date),
                    "session": attd.session.id
                    }
            attendance_list.append(data)
        return JsonResponse(json.dumps(attendance_list), safe=False)
    except Exception as e:
        return None


@require_POST
def get_user_profile_pic(request):
    """
    Returns user profile pic for the login page.
    SECURITY: Returns a generic avatar for ALL requests — never reveals
    whether an email exists in the system.
    """
    email = request.POST.get('email', '').strip()
    if not email:
        return JsonResponse({"status": "error", "message": "Please enter your email"})

    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"status": "error", "message": "Please enter a valid email address"})

    try:
        from .models import CustomUser
        users = CustomUser.objects.filter(email__iexact=email)
        if users.exists():
            user = users.first()
            full_name = f"{user.first_name} {user.last_name}".strip()
            if not full_name:
                full_name = "User"
            if user.profile_pic:
                url = user.profile_pic.url
            else:
                url = f"https://ui-avatars.com/api/?name={full_name}&background=6197e6&color=fff"
            return JsonResponse({"status": "success", "url": url, "full_name": full_name})
        else:
            # ── SECURITY: return a generic response, never confirm email doesn't exist ──
            return JsonResponse({
                "status": "success",
                "url": f"https://ui-avatars.com/api/?name=User&background=6197e6&color=fff",
                "full_name": "User"
            })

    except Exception:
        return JsonResponse({
            "status": "success",
            "url": f"https://ui-avatars.com/api/?name=User&background=6197e6&color=fff",
            "full_name": "User"
        })


def showFirebaseJS(request):
    data = """
    // Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here, other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config-object
firebase.initializeApp({
    apiKey: "AIzaSyBarDWWHTfTMSrtc5Lj3Cdw5dEvjAkFwtM",
    authDomain: "sms-with-django.firebaseapp.com",
    databaseURL: "https://sms-with-django.firebaseio.com",
    projectId: "sms-with-django",
    storageBucket: "sms-with-django.appspot.com",
    messagingSenderId: "945324593139",
    appId: "1:945324593139:web:03fa99a8854bbd38420c86",
    measurementId: "G-2F2RXTL9GT"
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
    const notification = JSON.parse(payload);
    const notificationOption = {
        body: notification.body,
        icon: notification.icon
    }
    return self.registration.showNotification(payload.notification.title, notificationOption);
});
    """
    return HttpResponse(data, content_type='application/javascript')
