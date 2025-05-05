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
            # First check if a profile already exists before creating one
            SurvivorProfile.objects.get_or_create(
                user=user,
                defaults={'bio': self.cleaned_data.get('bio', '')}
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
            # First check if a profile already exists before creating one
            CounselorProfile.objects.get_or_create(
                user=user,
                defaults={
                    'license_number': self.cleaned_data['license_number'],
                    'specialization': self.cleaned_data['specialization'],
                    'bio': self.cleaned_data['bio']
                }
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

class CounselorAvailabilityForm(forms.Form):
    DAYS_CHOICES = [(i, i) for i in range(1, 32)]  # Days in a month (1-31)
    CATEGORY_CHOICES = [
<<<<<<< HEAD
        ('domestic_violence', 'Domestic Violence'),
        ('child_abuse', 'Child Abuse'),
        ('sexual_abuse', 'Sexual Abuse'),
        ('trauma', 'Trauma'),
=======
        ('heart', 'Heart'),
        ('mental_health', 'Mental Health'),
>>>>>>> 860289cf76047db18ee215ffa04a0363f729ab43
        ('general', 'General'),
    ]

    days_available = forms.IntegerField(
        label="Days Available in a Month",
        min_value=1,
        max_value=31,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    category = forms.ChoiceField(
        label="Category",
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

class IncidentReportForm(forms.Form):
    incident_details = forms.CharField(
        label="Describe Your Incident",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Write about your incident here...',
            'rows': 5
        }),
    )
<<<<<<< HEAD
    schedule_date = forms.DateField(
        label="Schedule Counseling",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
    )
=======
>>>>>>> 860289cf76047db18ee215ffa04a0363f729ab43

class DonationForm(forms.Form):
    donor_name = forms.CharField(
        label="On Behalf Of",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your name or organization name'
        }),
    )
    amount = forms.DecimalField(
        label="Amount (in BDT)",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the amount you want to donate'
        }),
    )
    method = forms.ChoiceField(
        label="Payment Method",
        choices=[
            ('bkash', 'bKash'),
            ('nagad', 'Nagad'),
            ('bank', 'Bank Transfer'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

