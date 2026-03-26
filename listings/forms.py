from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .models import Property


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(required=True, label='Full name')
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

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if full_name and not re.match(r'^[a-zA-Z\s]*$', full_name):
            raise ValidationError('Full name can only contain characters and spaces.')
        return full_name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Must contain at least one letter and one number
            if not (re.search(r'[A-Za-z]', username) and re.search(r'\d', username)):
                raise ValidationError('Username must contain both letters and numbers.')
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1 and len(password1) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        return password1


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


class PropertyForm(forms.ModelForm):
    """Form for sellers to create and manage property listings"""
    
    # City-Area Mapping (matched with price prediction)
    CITY_AREA_MAPPING = {
        "Ahmedabad": ["Bopal", "Gota", "Maninagar"],
        "Gandhinagar": ["Infocity"],
        "Rajkot": ["Kalavad Road", "Mavdi", "Rajkot"],
        "Surat": ["Adajan", "Surat", "Varachha", "Vesu"],
        "Vadodara": ["Alkapuri", "Gotri", "Manjalpur"]
    }
    
    class Meta:
        model = Property
        fields = [
            'title', 'city', 'area', 'property_type', 
            'size_sqft', 'bedrooms', 'age_of_property_years',
            'nearby_infrastructure_score', 'distance_to_city_center_km',
            'price_inr'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Spacious Flat in Bopal',
                'required': True
            }),
            'city': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_city',
                'required': True
            }),
            'area': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_area',
                'required': True
            }),
            'property_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'size_sqft': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., 1200',
                'min': '100',
                'max': '10000',
                'required': True
            }),
            'bedrooms': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., 2',
                'min': '0',
                'max': '10',
                'required': True
            }),
            'age_of_property_years': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., 5',
                'min': '0',
                'max': '50',
                'required': True
            }),
            'nearby_infrastructure_score': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., 7',
                'min': '1',
                'max': '10',
                'required': True
            }),
            'distance_to_city_center_km': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., 8.5',
                'min': '0',
                'max': '50',
                'step': '0.1',
                'required': True
            }),
            'price_inr': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., 7500000',
                'min': '100000',
                'required': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Clear default initial values from model for a fresh look
        self.fields['bedrooms'].initial = ''
        self.fields['bedrooms'].required = False
        self.fields['age_of_property_years'].initial = ''
        self.fields['age_of_property_years'].required = False
        self.fields['nearby_infrastructure_score'].initial = ''
        self.fields['distance_to_city_center_km'].initial = ''
        
        self.fields['title'].required = True
        
        # Set up area field with choices based on selected city
        # Check both self.instance.city (editing) and self.data.get('city') (POST with errors)
        selected_city = None
        
        if self.instance and self.instance.city:
            # If editing an existing property
            selected_city = self.instance.city
        elif self.data and self.data.get('city'):
            # If form is bound (POST request with validation errors)
            selected_city = self.data.get('city')
        
        if selected_city and selected_city in self.CITY_AREA_MAPPING:
            area_choices = [(area, area) for area in self.CITY_AREA_MAPPING[selected_city]]
            self.fields['area'].choices = area_choices
        else:
            # Default: empty or just guidance
            self.fields['area'].choices = [('', 'Select City First')]
    
    def clean_price_inr(self):
        price = self.cleaned_data.get('price_inr')
        if price and price < 100000:
            raise ValidationError('Property price must be at least ₹1,00,000')
        return price
    
    def clean_size_sqft(self):
        size = self.cleaned_data.get('size_sqft')
        if size and (size < 100 or size > 10000):
            raise ValidationError('Property size must be between 100 and 10000 sq ft')
        return size
    
    def clean_city(self):
        city = self.cleaned_data.get('city')
        if city:
            # Ensure city matches valid choices
            valid_cities = [choice[0] for choice in self.Meta.model.CITY_CHOICES]
            if city not in valid_cities:
                raise ValidationError(f'Invalid city: {city}. Please select a valid city.')
        return city
    
    def clean_area(self):
        area = self.cleaned_data.get('area')
        city = self.cleaned_data.get('city')
        
        if area and city:
            # Ensure area is valid for selected city
            if city in self.CITY_AREA_MAPPING:
                valid_areas = self.CITY_AREA_MAPPING[city]
                if area not in valid_areas:
                    raise ValidationError(
                        f'"{area}" is not a valid locality for {city}. '
                        f'Please select from: {", ".join(valid_areas)}'
                    )
        elif not area and city:
            # Area is required if city is selected
            raise ValidationError('Please select a locality/area.')
        
        return area
    
    def clean_bedrooms(self):
        bedrooms = self.cleaned_data.get('bedrooms')
        property_type = self.cleaned_data.get('property_type')
        
        # For Plot properties, bedrooms can be 0
        # For other types, bedrooms must be specified
        if property_type and property_type != 'Plot':
            if bedrooms is None or bedrooms == '':
                raise ValidationError('Bedrooms is required for non-Plot properties.')
        
        return bedrooms
    
    def clean_age_of_property_years(self):
        age = self.cleaned_data.get('age_of_property_years')
        property_type = self.cleaned_data.get('property_type')
        
        # For Plot properties, age can be 0
        # For other types, age must be specified
        if property_type and property_type != 'Plot':
            if age is None or age == '':
                raise ValidationError('Age of Property is required for non-Plot properties.')
        
        return age
