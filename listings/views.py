from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .forms import SignupForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile
from django.views.decorators.csrf import ensure_csrf_cookie


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
        
        # Update user
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
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


