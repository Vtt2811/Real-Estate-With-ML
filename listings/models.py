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
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class BugReport(models.Model):
    """User-submitted bug reports or help requests"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bug_reports')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Bug from {self.user.username}: {self.subject}"


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
    views_count = models.IntegerField(default=0)

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
    
    def get_bedrooms_display(self):
        """Return formatted bedroom display string."""
        if self.bedrooms == 0:
            return "Studio/Plot"
        elif self.bedrooms == 1:
            return "1 BHK"
        elif self.bedrooms == 2:
            return "2 BHK"
        elif self.bedrooms == 3:
            return "3 BHK"
        elif self.bedrooms == 4:
            return "4 BHK"
        else:
            return f"{self.bedrooms} BHK"


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


class BuyerInterest(models.Model):
    """Tracks when a buyer shows interest in a property"""
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interests')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='interested_buyers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('buyer', 'property') # Prevent duplicate interests

    def __str__(self):
        return f"{self.buyer.username} interested in {self.property.title}"


class Message(models.Model):
    """Real-time chat messages between buyers and sellers"""
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"


# Message model (already defined at 164)
# Removing duplicated BugReport model from the end of the file.
