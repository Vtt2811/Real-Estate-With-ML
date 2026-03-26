from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .forms import SignupForm, AdminEmailChangeForm, PropertyForm
from django.contrib.auth.forms import AuthenticationForm
import json
import logging
import os
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import Profile, PasswordResetOTP, Property, BuyerInterest, Message, BugReport


@login_required(login_url='listings:signin')
def fetch_messages(request, receiver_id):
    """Fetch chat history between current user and another user"""
    receiver = get_object_or_404(User, id=receiver_id)
    
    # Get messages where (sender=user, receiver=other) OR (sender=other, receiver=user)
    messages_list = Message.objects.filter(
        (Q(sender=request.user, receiver=receiver) | 
         Q(sender=receiver, receiver=request.user))
    ).order_by('timestamp')
    
    # Mark messages as read
    messages_list.filter(receiver=request.user).update(is_read=True)
    
    data = [{
        'sender': msg.sender.username,
        'sender_id': msg.sender.id,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%H:%M'),
        'is_me': msg.sender == request.user
    } for msg in messages_list]
    
    return JsonResponse({'messages': data})


@login_required(login_url='listings:signin')
@require_POST
def send_message(request):
    """Send a new message to another user"""
    try:
        data = json.loads(request.body)
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        property_id = data.get('property_id')
        
        if not content:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
        receiver = get_object_or_404(User, id=receiver_id)
        prop = Property.objects.filter(id=property_id).first() if property_id else None
        
        msg = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            property=prop
        )
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'sender': msg.sender.username,
                'content': msg.content,
                'timestamp': msg.timestamp.strftime('%H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='listings:signin')
def messages_view(request):
    """Main messages dashboard showing all conversations"""
    # Get all direct messages where the user is either sender or receiver
    msgs = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
    
    # Identify unique users that have been chatted with
    other_user_ids = set()
    for m in msgs:
        # If chatting with self, still include it for testing
        if m.sender_id == m.receiver_id == request.user.id:
            other_user_ids.add(request.user.id)
        else:
            if m.sender_id != request.user.id:
                other_user_ids.add(m.sender_id)
            if m.receiver_id != request.user.id:
                other_user_ids.add(m.receiver_id)
            
    other_users = User.objects.filter(id__in=other_user_ids)
    
    # For each conversational partner, get the latest message and unread count
    chat_list = []
    for other in other_users:
        last_msg = Message.objects.filter(
            (Q(sender=request.user, receiver=other) | 
             Q(sender=other, receiver=request.user))
        ).order_by('timestamp').last()
        
        unread_count = Message.objects.filter(sender=other, receiver=request.user, is_read=False).count()
        
        chat_list.append({
            'user': other,
            'last_message': last_msg,
            'unread_count': unread_count
        })
    
    context = {
        'chat_list': sorted(chat_list, key=lambda x: x['last_message'].timestamp if x['last_message'] else None, reverse=True)
    }
    
    # Use different base depending on role or context
    # Allow URL parameter to switch between buyer and seller view contexts
    role_context = request.GET.get('view', request.user.profile.role)
    template = 'dashboards/messages_buyer.html' if role_context == 'buyer' else 'dashboards/messages_seller.html'
    
    return render(request, template, context)


logger = logging.getLogger(__name__)


def index(request):
    featured_properties = Property.objects.filter(is_active=True).order_by('-created_at')[:6]
    return render(request, 'index.html', {'featured_properties': featured_properties})


def listing_details(request):
    """Static property details page (reverted)"""
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
            except Exception as e:
                logger.warning(f"Error during logout in signup: {e}")
            return redirect('listings:signin')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


@ensure_csrf_cookie
def signin(request):
    # Allow the signin page to be viewed even if globally logged in 
    # to allow for per-tab session verification if needed.
    # if request.user.is_authenticated:
    #     return redirect('listings:index')
    
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
    except Exception as e:
        logger.warning(f"Error flushing session: {e}")
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


# Dashboard Views
@login_required(login_url='listings:signin')
def buyer_dashboard(request):
    """Buyer dashboard with property listings from the database and filters"""
    properties = Property.objects.filter(is_active=True)

    # --- Filtering ---
    city = request.GET.get('city', 'all')
    property_type = request.GET.get('property_type', 'all')
    price_range = request.GET.get('price', 'all')
    bedrooms = request.GET.get('bedrooms', 'all')
    search_area = request.GET.get('area', '').strip()

    if city != 'all':
        properties = properties.filter(city=city)
    if property_type != 'all':
        properties = properties.filter(property_type=property_type)
    if bedrooms != 'all':
        try:
            properties = properties.filter(bedrooms=int(bedrooms))
        except ValueError:
            pass
    if search_area:
        properties = properties.filter(area__icontains=search_area)

    if price_range != 'all':
        if price_range == 'under50':
            properties = properties.filter(price_inr__lt=5000000)
        elif price_range == '50to1cr':
            properties = properties.filter(price_inr__gte=5000000, price_inr__lte=10000000)
        elif price_range == '1crto2cr':
            properties = properties.filter(price_inr__gte=10000000, price_inr__lte=20000000)
        elif price_range == 'above2cr':
            properties = properties.filter(price_inr__gt=20000000)

    # --- Pagination (24 per page) ---
    paginator = Paginator(properties, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # --- Stats ---
    total_properties = Property.objects.filter(is_active=True).count()

    # Filter choices for the template
    cities = Property.CITY_CHOICES
    property_types = Property.PROPERTY_TYPE_CHOICES

    # Get a list of IDs the user is interested in for initial card styling
    interested_property_ids = list(BuyerInterest.objects.filter(buyer=request.user).values_list('property_id', flat=True))

    # Identify if a chat is started between buyer and any sellers
    chatted_user_ids = set(Message.objects.filter(sender=request.user).values_list('receiver_id', flat=True)) | \
                      set(Message.objects.filter(receiver=request.user).values_list('sender_id', flat=True))

    context = {
        'page_obj': page_obj,
        'properties': page_obj.object_list,
        'total_properties': total_properties,
        'filtered_count': paginator.count,
        'interested_property_ids': interested_property_ids,
        'chatted_user_ids': chatted_user_ids,
        # Current filter values
        'current_city': city,
        'current_property_type': property_type,
        'current_price': price_range,
        'current_bedrooms': bedrooms,
        'current_area': search_area,
        # Choices
        'cities': cities,
        'property_types': property_types,
    }
    return render(request, 'dashboards/buyer_dashboard.html', context)


@login_required(login_url='listings:signin')
def seller_dashboard(request):
    """Seller dashboard overview"""
    if request.user.profile.role != 'seller':
        return redirect('listings:buyer_dashboard')
        
    # Get user's properties (My Listings)
    user_properties = Property.objects.filter(seller=request.user, is_active=True).order_by('-created_at')
    # Fetch interests for properties owned by this seller
    recent_interests = BuyerInterest.objects.filter(property__seller=request.user).order_by('-created_at')[:10]
    
    # Calculate total views for all seller's properties
    from django.db.models import Sum
    total_views = user_properties.aggregate(Sum('views_count'))['views_count__sum'] or 0
    
    context = {
        'user_properties': user_properties,
        'property_count': user_properties.count(),
        'total_views': total_views,
        'recent_interests': recent_interests,
    }
    return render(request, 'dashboards/seller_dashboard.html', context)


@login_required(login_url='listings:signin')
def add_property(request):
    """Dedicated page for adding a new property"""
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            # Create property with current user as seller
            property_obj = form.save(commit=False)
            property_obj.seller = request.user
            # Automatically calculate Built Year based on Age
            # Current Platform Year: 2026
            property_obj.year = 2026 - property_obj.age_of_property_years
            property_obj.save()
            messages.success(request, f'Property "{property_obj.title}" added successfully! View it in My Listings.')
            return redirect('listings:add_property')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PropertyForm()
    
    context = {
        'form': form,
    }
    return render(request, 'dashboards/add_property.html', context)


@login_required(login_url='listings:signin')
def my_listings(request):
    """Display all properties added by the seller (read-only)"""
    user_properties = Property.objects.filter(seller=request.user, is_active=True).order_by('-created_at')
    
    context = {
        'user_properties': user_properties,
        'property_count': user_properties.count(),
    }
    return render(request, 'dashboards/my_listings.html', context)


@login_required(login_url='listings:signin')
def price_prediction(request):
    """Separate page for ML price prediction"""
    return render(request, 'dashboards/price_prediction.html')


@login_required(login_url='listings:signin')
def edit_property(request, pk):
    """Edit an existing property"""
    property_obj = get_object_or_404(Property, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property_obj)
        if form.is_valid():
            property_obj = form.save(commit=False)
            # Automatically calculate/update Built Year based on Age
            property_obj.year = 2026 - property_obj.age_of_property_years
            property_obj.save()
            messages.success(request, f'Property "{property_obj.title}" updated successfully!')
            return redirect('listings:my_listings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PropertyForm(instance=property_obj)
    
    context = {
        'form': form,
        'is_edit': True,
        'property': property_obj,
    }
    return render(request, 'dashboards/add_property.html', context)


@login_required(login_url='listings:signin')
@require_POST
def delete_property(request, pk):
    """Delete (deactivate) a property"""
    property_obj = get_object_or_404(Property, pk=pk, seller=request.user)
    property_obj.is_active = False
    property_obj.save()
    messages.success(request, f' Property "{property_obj.title}" deleted successfully.')
    return redirect('listings:my_listings')


@login_required(login_url='listings:signin')
def property_details_api(request, pk):
    """API endpoint: return property details in JSON format and increment view count."""
    property_obj = get_object_or_404(Property, pk=pk)
    
    # Increment views count
    property_obj.views_count += 1
    property_obj.save(update_fields=['views_count'])
    
    data = {
        'title': property_obj.title,
        'city': property_obj.city,
        'area': property_obj.area,
        'property_type': property_obj.property_type,
        'size_sqft': property_obj.size_sqft,
        'bedrooms': property_obj.get_bedrooms_display() if property_obj.property_type != 'Plot' else 'None (Plot)',
        'age': f"{property_obj.age_of_property_years} years",
        'infrastructure': f"{property_obj.nearby_infrastructure_score}/10",
        'distance': f"{property_obj.distance_to_city_center_km} km",
        'year': 2026 - property_obj.age_of_property_years,
        'price': property_obj.formatted_price,
        'full_price': f"₹{property_obj.price_inr:,}",
        'is_interested': BuyerInterest.objects.filter(buyer=request.user, property=property_obj).exists(),
        'id': property_obj.id,
        'seller_id': property_obj.seller.id,
        'seller_name': property_obj.seller.username,
        'has_chat': Message.objects.filter(
            (Q(sender=request.user, receiver=property_obj.seller) | 
             Q(sender=property_obj.seller, receiver=request.user))
        ).exists()
    }
    return JsonResponse(data)


@login_required(login_url='listings:signin')
@require_POST
def toggle_interest(request, pk):
    """Register buyer's interest in a property"""
    if request.user.profile.role != 'buyer':
        return JsonResponse({'error': 'Only buyers can show interest.'}, status=403)
        
    property_obj = get_object_or_404(Property, pk=pk)
    # Check if the buyer already showed interest
    interest = BuyerInterest.objects.filter(buyer=request.user, property=property_obj).first()
    
    if interest:
        interest.delete()
        return JsonResponse({'status': 'removed'})
    
    BuyerInterest.objects.create(buyer=request.user, property=property_obj)
    return JsonResponse({'status': 'added'})


# --- ML Price Prediction ---
_ml_pipeline = None

def _get_pipeline():
    """Load the ML pipeline once and cache it."""
    global _ml_pipeline
    if _ml_pipeline is None:
        import joblib
        from django.conf import settings
        pkl_path = os.path.join(settings.BASE_DIR, 'ML_pipeline.pkl')
        _ml_pipeline = joblib.load(pkl_path)
        logger.info('ML pipeline loaded from %s', pkl_path)
    return _ml_pipeline


@login_required(login_url='listings:signin')
@require_POST
def predict_price(request):
    """API endpoint: predict property price using the ML pipeline.

    Expects a JSON body with keys matching the pipeline features:
      City, Area, Property_Type, Size_sqft, Bedrooms,
      Age_of_Property_years, Distance_to_City_Center_km, Year
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    required = [
        'City', 'Area', 'Property_Type', 'Size_sqft',
        'Bedrooms', 'Age_of_Property_years',
        'Distance_to_City_Center_km', 'Year',
    ]
    missing = [f for f in required if f not in data]
    if missing:
        return JsonResponse({'error': f'Missing fields: {", ".join(missing)}'}, status=400)

    try:
        import pandas as pd
        input_df = pd.DataFrame([{
            'City': data['City'],
            'Area': data['Area'],
            'Property_Type': data['Property_Type'],
            'Size_sqft': int(data['Size_sqft']),
            'Bedrooms': int(data['Bedrooms']),
            'Age_of_Property_years': int(data['Age_of_Property_years']),
            'Distance_to_City_Center_km': float(data['Distance_to_City_Center_km']),
            'Year': int(data['Year']),
        }])

        pipeline = _get_pipeline()
        prediction = pipeline.predict(input_df)
        predicted_price = round(float(prediction[0]), 2)

        # Format for display
        if predicted_price >= 10000000:
            formatted = f'₹{predicted_price / 10000000:.2f} Cr'
        elif predicted_price >= 100000:
            formatted = f'₹{predicted_price / 100000:.2f} L'
        else:
            formatted = f'₹{predicted_price:,.0f}'

        return JsonResponse({
            'predicted_price': predicted_price,
            'formatted_price': formatted,
        })
    except Exception as e:
        logger.error('Prediction error: %s', e, exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)



def dashboard_directory(request):
    """Dashboard directory page for easy navigation"""
    return render(request, 'dashboards/dashboard_directory.html')


# OTP-based Password Reset Views

def request_password_reset_otp(request):
    """Request OTP for password reset"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        try:
            user = User.objects.get(email=email)
            
            # Invalidate any existing OTPs for this user
            # Invalidate any existing OTPs for this user
            PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Create new OTP
            otp_instance = PasswordResetOTP.objects.create(user=user)
            
            # Print OTP to Console (DEBUGGING)
            # Log OTP (DEBUGGING - In production, log only generation event, not the code)
            logger.info(f"OTP GENERATED FOR: {email} | CODE: {otp_instance.otp}")
            
            # Send OTP via email
            subject = 'Password Reset OTP - Home Finder'
            message = f'''Hello {user.username},

You have requested to reset your password. Your OTP is:

{otp_instance.otp}

This OTP will expire in 10 minutes.

If you did not request this, please ignore this email.

Best regards,
Home Finder Team'''
            
            try:
                send_mail(
                    subject,
                    message,
                    'noreply@realestate.com',
                    [email],
                    fail_silently=False,
                )
                # DEBUG: SHOW OTP ON SCREEN FOR TESTING
                messages.success(request, f'✅ DEBUG MODE: Your OTP is {otp_instance.otp}')
                
                request.session['reset_email'] = email
                return redirect('listings:verify_password_reset_otp')
            except Exception as e:
                logger.error(f"Error sending email: {e}")
                logger.error(f"Failed to send OTP email: {e}")
                messages.error(request, 'Failed to send OTP. Please try again later.')
        
        except User.DoesNotExist:
            logger.warning(f"User with email '{email}' NOT FOUND during password reset request.")
            # Don't reveal if email exists or not for security
            messages.info(request, 'If an account with this email exists, an OTP has been sent.')
            return redirect('listings:verify_password_reset_otp')
    
    return render(request, 'password_reset/request_otp.html')


def verify_password_reset_otp(request):
    """Verify OTP and allow password reset"""
    email = request.session.get('reset_email')
    
    if not email:
        messages.error(request, 'Please request an OTP first.')
        return redirect('listings:request_password_reset_otp')
    
    if request.method == 'POST':
        otp_entered = request.POST.get('otp', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Validate passwords match
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'password_reset/verify_otp.html', {'email': email})
        
        # Validate password length
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'password_reset/verify_otp.html', {'email': email})
        
        try:
            user = User.objects.get(email=email)
            # Get the latest unused OTP for this user
            otp_instance = PasswordResetOTP.objects.filter(
                user=user,
                otp=otp_entered,
                is_used=False
            ).first()
            
            if otp_instance and otp_instance.is_valid():
                # OTP is valid, reset password
                user.set_password(new_password)
                user.save()
                
                # Mark OTP as used
                otp_instance.is_used = True
                otp_instance.save()
                
                # Clear session
                if 'reset_email' in request.session:
                    del request.session['reset_email']
                
                messages.success(request, 'Password reset successful! You can now login with your new password.')
                return redirect('listings:signin')
            else:
                messages.error(request, 'Invalid or expired OTP. Please try again.')
        
        except User.DoesNotExist:
            messages.error(request, 'Invalid request.')
            return redirect('listings:request_password_reset_otp')
    
    return render(request, 'password_reset/verify_otp.html', {'email': email})
@login_required(login_url='listings:signin')
def admin_dashboard(request):
    """Main dashboard for administrators"""
    # Auto-create profile for superusers if missing
    if not hasattr(request.user, 'profile') and request.user.is_superuser:
        # Avoid circular import or assure Profile is available
        from .models import Profile
        Profile.objects.create(user=request.user, role='admin')
        
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, "Access denied. Admins only.")
        return redirect('listings:index')
    
    # Statistics
    total_users = User.objects.count()
    total_listings = Property.objects.count()
    total_bugs = BugReport.objects.count()
    total_messages = Message.objects.count()
    
    # Recent items
    recent_users = User.objects.exclude(username=request.user.username).order_by('-date_joined')[:5]
    recent_listings = Property.objects.all().order_by('-created_at')[:5]
    pending_bugs = BugReport.objects.filter(status='pending').order_by('-created_at')
    
    # Build Activity Feed
    feed = []
    # Bugs
    for b in BugReport.objects.all().order_by('-created_at')[:8]:
        feed.append({
            'type': b.get_status_display(),
            'title': f"Report: {b.subject}",
            'user': b.user.username,
            'time': b.created_at,
            'icon': 'alert-circle'
        })
    # Listings
    for p in Property.objects.all().order_by('-created_at')[:8]:
        feed.append({
            'type': 'Listing',
            'title': f"Added: {p.title or p.property_type}",
            'user': p.seller.username if p.seller else 'System',
            'time': p.created_at,
            'icon': 'home'
        })
    # Sort activity by time
    feed.sort(key=lambda x: x['time'], reverse=True)
    
    context = {
        'total_users': total_users,
        'total_listings': total_listings,
        'total_bugs': total_bugs,
        'total_messages': total_messages,
        'recent_users': recent_users,
        'recent_listings': recent_listings,
        'pending_bugs': pending_bugs,
        'activities': feed[:12]
    }
    return render(request, 'dashboards/admin_dashboard.html', context)

@login_required(login_url='listings:signin')
@require_POST
def report_bug(request):
    """API endpoint for users to submit feedback or bug reports"""
    try:
        data = json.loads(request.body)
        subject = data.get('subject')
        description = data.get('description')
        
        if not subject or not description:
            return JsonResponse({'error': 'Please provide both subject and description.'}, status=400)
            
        bug = BugReport.objects.create(
            user=request.user,
            subject=subject,
            description=description
        )
        return JsonResponse({'status': 'success', 'message': 'Report submitted!'})
    except Exception as e:
        return JsonResponse({'error': f'Failed to submit: {str(e)}'}, status=500)

@login_required(login_url='listings:signin')
@require_POST
def resolve_bug(request, bug_id):
    """Admin endpoint to mark bugs as resolved"""
    if request.user.profile.role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    bug = get_object_or_404(BugReport, id=bug_id)
    bug.status = 'resolved'
    bug.resolved_at = timezone.now()
    bug.save()
    return JsonResponse({'status': 'success'})

@login_required(login_url='listings:signin')
@require_POST
def resolve_all_bugs(request):
    """Admin endpoint to mark all bugs as resolved"""
    if request.user.profile.role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    # Find the BugReport model dynamically if needed, or assume it's imported
    from .models import BugReport
    BugReport.objects.filter(status='pending').update(
        status='resolved', 
        resolved_at=timezone.now()
    )
    return JsonResponse({'status': 'success'})
