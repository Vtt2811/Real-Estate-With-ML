from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
import string


class Profile(models.Model):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Property(models.Model):
    """Property listing model matching the Future_Trend_Dataset_100K dataset."""

    CITY_CHOICES = (
        ('Ahmedabad', 'Ahmedabad'),
        ('Gandhinagar', 'Gandhinagar'),
        ('Rajkot', 'Rajkot'),
        ('Surat', 'Surat'),
        ('Vadodara', 'Vadodara'),
    )

    PROPERTY_TYPE_CHOICES = (
        ('Flat', 'Flat'),
        ('House', 'House'),
        ('Plot', 'Plot'),
    )

    # Optional seller (null for dataset-imported properties)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='properties'
    )
    title = models.CharField(max_length=200, blank=True, default='')

    # Dataset fields
    city = models.CharField(max_length=50, choices=CITY_CHOICES)
    area = models.CharField(max_length=100)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    size_sqft = models.IntegerField()
    bedrooms = models.IntegerField(default=0)
    age_of_property_years = models.IntegerField(default=0)
    nearby_infrastructure_score = models.IntegerField(default=5)
    distance_to_city_center_km = models.FloatField(default=0.0)
    year = models.IntegerField(default=2024)
    price_inr = models.BigIntegerField()

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'

    def __str__(self):
        label = self.title or f"{self.property_type} in {self.area}, {self.city}"
        return f"{label} — ₹{self.price_inr:,}"

    @property
    def formatted_price(self):
        """Return Indian-formatted price string."""
        p = self.price_inr
        if p >= 10000000:
            return f"₹{p / 10000000:.2f} Cr"
        elif p >= 100000:
            return f"₹{p / 100000:.2f} L"
        else:
            return f"₹{p:,}"


class PasswordResetOTP(models.Model):
    """Model to store OTPs for password reset"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            # Generate 6-digit OTP
            self.otp = ''.join(random.choices(string.digits, k=6))
            # Set expiration to 10 minutes from now
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp}"
    
    class Meta:
        ordering = ['-created_at']
