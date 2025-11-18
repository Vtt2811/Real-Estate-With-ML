from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(required=False, label='Full name')
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, initial='buyer')

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        # role is handled separately (Profile)
        full_name = self.cleaned_data.get('full_name')
        if full_name:
            parts = full_name.split(None, 1)
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = parts[1]
        if commit:
            user.save()
        return user

    def clean_email(self):
        """Ensure email addresses are unique (case-insensitive)."""
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip()
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError('An account with this email already exists.')
        return email


class AdminEmailChangeForm(forms.Form):
    email = forms.EmailField(required=True)

    def __init__(self, *args, user_obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_obj = user_obj

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip()
            qs = User.objects.filter(email__iexact=email)
            if self.user_obj:
                qs = qs.exclude(pk=self.user_obj.pk)
            if qs.exists():
                raise ValidationError('An account with this email already exists.')
        return email
