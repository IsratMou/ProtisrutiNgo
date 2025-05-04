from .models import CustomUser, SurvivorProfile, Counselor
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms


from django.shortcuts import render, redirect


class SurvivorRegistrationForm(UserCreationForm):
    """
    Form for survivor registration with custom fields
    """
    email = forms.CharField(
        max_length=254,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'placeholder': 'Tell us about yourself (optional)', 'rows': 3})
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'survivor'

        if commit:
            user.save()
            SurvivorProfile.objects.get_or_create(
                user=user,
                defaults={'bio': self.cleaned_data.get('bio', '')}
            )
        return user


class CounselorRegistrationForm(forms.ModelForm):
    """
    Form for counselor registration with additional fields
    """
    EXPERTISE_CHOICES = [
        ('trauma_ptsd', 'Trauma & PTSD Counseling'),
        ('child_abuse', 'Child & Adolescent Abuse Counseling'),
        ('domestic_violence', 'Domestic Violence Counseling'),
        ('ipv', 'Intimate Partner Violence (IPV) Counseling'),
        ('mental_health', 'Mental Health Counseling'),
        ('career_guidance', 'Career Guidance'),
        ('relationship_counseling', 'Relationship Counseling'),
        ('financial_advice', 'Financial Advice'),
        ('addiction_recovery', 'Addiction Recovery'),
        ('sexual_abuse', 'Sexual Abuse and Harassment Counseling'),
    ]

    email = forms.CharField(
        max_length=254,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    expertise_sector = forms.ChoiceField(
        choices=EXPERTISE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Expertise Sector"
    )

    class Meta:
        model = Counselor
        fields = ['name', 'email', 'years_of_experience', 'expertise_sector']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of Experience'}),
        }


class CustomLoginForm(AuthenticationForm):
    """
    Custom login form with styled fields
    """
    username = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


def register_counselor_view(request):
    """
    View for counselor registration
    """
    if request.method == 'POST':
        form = CounselorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')  # Replace with your success URL
    else:
        form = CounselorRegistrationForm()
    return render(request, 'register_counselor.html', {'form': form})
