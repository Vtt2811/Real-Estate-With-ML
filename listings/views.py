from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .forms import SignupForm, AdminEmailChangeForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponseForbidden
import logging
from django.contrib.admin.views.decorators import staff_member_required

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'index.html')


def listing_details(request):
    return render(request, 'listing-details.html')


@ensure_csrf_cookie
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create profile with role chosen during signup
            role = form.cleaned_data.get('role')
            Profile.objects.create(user=user, role=role, email_verified=True)
            
            messages.success(request, 'Sign-up successful! You can now sign in.')
            # Ensure any existing session is cleared so the next page (signin)
            # is rendered for an anonymous user. This prevents accidental
            # display of the index page when the signin view redirects
            # authenticated users to the home page.
            try:
                logout(request)
            except Exception:
                pass
            return redirect('listings:signin')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


@ensure_csrf_cookie
def signin(request):
    if request.user.is_authenticated:
        return redirect('listings:index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Rotate the session key after successful login to avoid session
            # fixation issues and ensure any previous session data cannot be
            # reused for the newly authenticated user.
            try:
                request.session.cycle_key()
            except Exception:
                pass
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('listings:index')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'signin.html', {'form': form})


def signout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    # Ensure the session is fully flushed after logout to avoid lingering
    # session data that could cause another user to appear logged in.
    try:
        request.session.flush()
    except Exception:
        pass
    return redirect('listings:index')


@login_required(login_url='listings:signin')
def profile(request):
    """User profile page with editable information"""
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='buyer')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        role = request.POST.get('role', profile.role)
        
        # Validate email
        if email and email != request.user.email:
            if request.user.__class__.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.error(request, 'This email is already in use.')
                return render(request, 'profile.html', {'profile': profile})
        
        # Update user only when values are provided. This prevents an empty
        # form field from overwriting an existing value (e.g. last name).
        if first_name:
            request.user.first_name = first_name
        # Only update last_name when the user explicitly provides a non-empty value
        if last_name:
            request.user.last_name = last_name
        # Email is immutable for users: do NOT update request.user.email here.
        request.user.save()
        
        # Update profile
        profile.role = role
        profile.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('listings:profile')
    
    context = {
        'profile': profile,
        'user': request.user,
    }
    return render(request, 'profile.html', context)


def csrf_failure(request, reason=""):
    """Custom CSRF failure view to log useful debug information.

    This is configured only for development to help diagnose token/cookie
    mismatches. It logs relevant request META entries (without exposing
    sensitive session data) and returns a simple 403 response.
    """
    # Log a few keys that help diagnose CSRF problems.
    info = {
        'reason': reason,
        'host': request.get_host(),
        'path': request.path,
        'referer': request.META.get('HTTP_REFERER'),
        'cookie_keys': list(request.COOKIES.keys()),
        'csrf_cookie': request.COOKIES.get('csrftoken'),
        'csrf_header': request.META.get('HTTP_X_CSRFTOKEN'),
        'remote_addr': request.META.get('REMOTE_ADDR'),
    }
    logger.warning('CSRF failure: %s', info)
    # Also print to stdout so it's visible in the runserver console for quick debugging
    try:
        print('\n[CSRF FAILURE DEBUG] %s\n' % info)
    except Exception:
        pass

    # Return a minimal 403 page with a friendly message during development.
    body = (
        "CSRF verification failed. Reason: %s\n"
        "Please ensure cookies are enabled, reload the form page, and try again."
    ) % (reason or 'unknown')
    return HttpResponseForbidden(body, content_type='text/plain')


@staff_member_required
def admin_change_email(request, user_id):
    """Admin-only view to change a user's email address.

    Only accessible to staff members. Validates uniqueness and updates the
    target user's email on success.
    """
    target = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = AdminEmailChangeForm(request.POST, user_obj=target)
        if form.is_valid():
            new_email = form.cleaned_data['email']
            target.email = new_email
            target.save()
            messages.success(request, f"Email for {target.username} has been updated.")
            # Redirect to the admin user change page for convenience
            try:
                return redirect(reverse('admin:auth_user_change', args=[target.pk]))
            except Exception:
                return redirect('listings:profile')
    else:
        form = AdminEmailChangeForm(initial={'email': target.email}, user_obj=target)

    return render(request, 'admin_change_email.html', {'form': form, 'target': target})


