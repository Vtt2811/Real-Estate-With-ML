from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'listings'

urlpatterns = [
    path('', views.index, name='index'),
    path('listing-details/', views.listing_details, name='listing_details'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
     path('profile/', views.profile, name='profile'),
     # Admin helper to change a user's email (staff-only)
     path('admin/change-email/<int:user_id>/', views.admin_change_email, name='admin_change_email'),
    
    # OTP-based Password Reset (NEW)
    path('forgot-password/', views.request_password_reset_otp, name='request_password_reset_otp'),
    path('verify-otp/', views.verify_password_reset_otp, name='verify_password_reset_otp'),
    
    # Password reset flow (uses console email backend in settings)
     path('password-reset/',
           auth_views.PasswordResetView.as_view(
                template_name='registration/password_reset_form.html',
                success_url=reverse_lazy('listings:password_reset_done')
           ),
           name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
     path('reset/done/',
          auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
          name='password_reset_complete'),
     
     # Dashboard URLs
     path('dashboards/', views.dashboard_directory, name='dashboard_directory'),
     path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
     path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
     path('platform-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

     
     # Redirect /dashboard/ to /dashboards/ for convenience
     path('dashboard/', views.dashboard_directory, name='dashboard_alias'),
]
