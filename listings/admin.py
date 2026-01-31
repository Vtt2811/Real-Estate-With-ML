from django.contrib import admin
from .models import Profile, PasswordResetOTP


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    search_fields = ('user__username', 'user__email')


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email', 'otp')
    readonly_fields = ('otp', 'created_at', 'expires_at')
