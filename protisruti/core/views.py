from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import HttpResponse
from .forms import SurvivorRegistrationForm, CounselorRegistrationForm, CustomLoginForm, CounselorAvailabilityForm, IncidentReportForm, DonationForm
from .models import CustomUser

def home_view(request):
    """View for the homepage"""
    return render(request, 'home.html')

class LoginOptionsView(TemplateView):
    """View to choose between survivor and counselor login"""
    template_name = 'login_options.html'

def login_view(request):
    """View for user login"""
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('login_redirect')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

def login_redirect_view(request):
    """Redirects users based on their user type after login"""
    if request.user.is_survivor():
        return redirect('user_dashboard')
    elif request.user.is_counselor():
        return redirect('counselor_dashboard')
    else:
        return redirect('home')

def register_user_view(request):
    """View for survivor registration"""
    if request.method == 'POST':
        form = SurvivorRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Account created successfully! You can now log in.')
                return redirect('login')
            except Exception as e:
                # Handle database errors gracefully
                messages.error(request, f'Registration failed. Please try again or contact support.')
                print(f"Error during survivor registration: {str(e)}")
    else:
        form = SurvivorRegistrationForm()
    return render(request, 'register_user.html', {'form': form})

def register_counselor_view(request):
    """View for counselor registration"""
    if request.method == 'POST':
        form = CounselorRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Your registration has been submitted. Our admin will review your credentials.')
                return redirect('login')
            except Exception as e:
                # Handle database errors gracefully
                messages.error(request, f'Registration failed. Please try again or contact support.')
                print(f"Error during counselor registration: {str(e)}")
    else:
        form = CounselorRegistrationForm()
    return render(request, 'register_counselor.html', {'form': form})

@login_required
def user_dashboard(request):
    """View for survivor dashboard"""
    if request.method == 'POST':
        form = IncidentReportForm(request.POST)
        if form.is_valid():
            # Process the form data
            incident_details = form.cleaned_data['incident_details']
            # Save the data or perform any action (e.g., save to database)
            messages.success(request, "Your incident report has been submitted. A counselor will contact you soon.")
            return redirect('user_dashboard')
    else:
        form = IncidentReportForm()

    return render(request, 'user_dashboard.html', {'form': form})

@login_required
def counselor_dashboard(request):
    """View for counselor dashboard"""
    if request.method == 'POST':
        form = CounselorAvailabilityForm(request.POST)
        if form.is_valid():
            # Process the form data
            days_available = form.cleaned_data['days_available']
            category = form.cleaned_data['category']
            # Save the data or perform any action
            return HttpResponse("Form submitted successfully!")
    else:
        form = CounselorAvailabilityForm()

    return render(request, 'counselor_dashboard.html', {'form': form})

def donation_view(request):
    """View for the donation form"""
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            # Process the donation data
            donor_name = form.cleaned_data['donor_name']
            amount = form.cleaned_data['amount']
            method = form.cleaned_data['method']
            # You can save this data to the database or process it further
            messages.success(request, f"Thank you, {donor_name}, for your generous donation of BDT {amount} via {method}!")
            return redirect('donation')
    else:
        form = DonationForm()

    return render(request, 'donation.html', {'form': form})