from django import forms
from django.contrib.auth.models import User
import re

class VoterSignupForm(forms.Form):
    nic = forms.CharField(
        label='SLIN/NIC', 
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your NIC (e.g., 123456789V or 199912345678)',
            'class': 'form-control'
        })
    )
    mobile_number = forms.CharField(
        label='Mobile Number', 
        max_length=15,
        widget=forms.TextInput(attrs={
            'placeholder': '+94 XX XXX XXXX or 0XX XXX XXXX',
            'class': 'form-control'
        })
    )
    name = forms.CharField(
        label='Name', 
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your full name',
            'class': 'form-control'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter a strong password',
            'class': 'form-control'
        }), 
        label='Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Re-enter your password',
            'class': 'form-control'
        }), 
        label='Confirm Password'
    )

    def clean_nic(self):
        nic = self.cleaned_data.get('nic', '').strip()
        from .db_utils import validate_temp_nic
        
        is_valid, status, message = validate_temp_nic(nic)
        if not is_valid:
            raise forms.ValidationError(message)
        
        return nic.upper()

    
    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number', '').strip()
        
        # Remove spaces
        mobile_clean = mobile.replace(' ', '')
        
        # Validate Sri Lankan mobile format
        # Accepts: +94XXXXXXXXX or 0XXXXXXXXX
        pattern = re.match(r'^(\+94|0)[0-9]{9}$', mobile_clean)
        
        if not pattern:
            raise forms.ValidationError(
                "Invalid mobile number. Use format: +94XXXXXXXXX or 0XXXXXXXXX"
            )
        
        return mobile

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data



class VoterRegistrationForm(forms.Form):
    DISTRICTS = [
        ('Ampara', 'Ampara'), ('Anuradhapura', 'Anuradhapura'), ('Badulla', 'Badulla'), 
        ('Batticaloa', 'Batticaloa'), ('Colombo', 'Colombo'), ('Galle', 'Galle'), 
        ('Gampaha', 'Gampaha'), ('Hambantota', 'Hambantota'), ('Jaffna', 'Jaffna'), 
        ('Kalutara', 'Kalutara'), ('Kandy', 'Kandy'), ('Kegalle', 'Kegalle'), 
        ('Kilinochchi', 'Kilinochchi'), ('Kurunegala', 'Kurunegala'), ('Mannar', 'Mannar'), 
        ('Matale', 'Matale'), ('Matara', 'Matara'), ('Monaragala', 'Monaragala'), 
        ('Mullaitivu', 'Mullaitivu'), ('Nuwara Eliya', 'Nuwara Eliya'), ('Polonnaruwa', 'Polonnaruwa'), 
        ('Puttalam', 'Puttalam'), ('Ratnapura', 'Ratnapura'), ('Trincomalee', 'Trincomalee'), 
        ('Vavuniya', 'Vavuniya')
    ]

    # Editable fields (pre-filled from signup)
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter full name',
            'class': 'form-control'
        })
    )
    nic = forms.CharField(
        label='SLIN/NIC',
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter NIC',
            'class': 'form-control'
        })
    )
    email = forms.EmailField(
        required=False,
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'placeholder': 'voter@example.com',
            'class': 'form-control'
        })
    )
    mobile_number = forms.CharField(
        required=False,
        label='Mobile Number',
        max_length=15,
        widget=forms.TextInput(attrs={
            'placeholder': '+94XXXXXXXXX or 07XXXXXXXX',
            'class': 'form-control'
        })
    )
    
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    gender = forms.ChoiceField(
        choices=[('Male', 'Male'), ('Female', 'Female')], 
        widget=forms.RadioSelect
    )
    election_year = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., 2026',
            'class': 'form-control'
        })
    )
    election_district = forms.ChoiceField(
        choices=DISTRICTS, 
        widget=forms.RadioSelect
    )
    admin_district = forms.ChoiceField(
        choices=DISTRICTS, 
        widget=forms.RadioSelect
    )
    polling_division = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter polling division',
            'class': 'form-control'
        })
    )
    postal_code = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter postal code',
            'class': 'form-control'
        })
    )
    grama_niladari_division = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Grama Niladari Division',
            'class': 'form-control'
        })
    )
    village_street = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter village or street',
            'class': 'form-control'
        })
    )
    household = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter household number',
            'class': 'form-control'
        })
    )

    def clean_election_year(self):
        year = self.cleaned_data.get('election_year')
        if not year:
            from datetime import datetime
            return str(datetime.now().year)
        return year.strip()

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            from datetime import date
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise forms.ValidationError(
                    f"You must be at least 18 years old to register. You are currently {age} years old."
                )
        return dob

