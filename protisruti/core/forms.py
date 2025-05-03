from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, SurvivorProfile, CounselorProfile

class SurvivorRegistrationForm(UserCreationForm):
    """
    Form for survivor registration with custom fields
    """
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell us about yourself (optional)', 'rows': 3})
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'survivor'
        
        if commit:
            user.save()
            SurvivorProfile.objects.create(
                user=user,
                bio=self.cleaned_data.get('bio', '')
            )
        return user

class CounselorRegistrationForm(UserCreationForm):
    """
    Form for counselor registration with professional details
    """
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    license_number = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'License Number'})
    )
    specialization = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specialization'})
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell us about your experience', 'rows': 3})
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'counselor'
        
        if commit:
            user.save()
            CounselorProfile.objects.create(
                user=user,
                license_number=self.cleaned_data['license_number'],
                specialization=self.cleaned_data['specialization'],
                bio=self.cleaned_data['bio']
            )
        return user

class CustomLoginForm(AuthenticationForm):
    """
    Custom login form with styled fields
    """
    username = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )