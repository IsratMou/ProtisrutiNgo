from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_http_methods

from .forms import (
    CounselorVerificationForm,
    CounselorProfileForm,
    UserRegistrationForm,  # Will be defined in forms.py
    CounselorRegistrationForm,
    LoginForm,
)
from .models import CounselorProfile, Assignment


def is_admin(user):
    """Check if a user has admin privileges"""
    return user.is_superuser or user.user_type == 'admin'


def is_counselor(user):
    """Check if user is a counselor"""
    return user.user_type == 'counselor' and user.counselorprofile.is_verified


def home_view(request):
    """Home page view"""
    return render(request, 'home.html')


class LoginOptionsView(View):
    """View to display login options for different user types"""

    @staticmethod
    def get(request):
        return render(request, 'login_options.html')


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('login_redirect')
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def login_redirect_view(request):
    """Redirect users to appropriate dashboard based on user type"""
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.user_type == 'survivor':
        return redirect('user_dashboard')
    elif request.user.user_type == 'counselor':
        return redirect('counselor_dashboard')
    elif request.user.is_superuser or request.user.user_type == 'admin':
        return redirect('admin:index')
    else:
        # Default fallback
        return redirect('home')


def register_user_view(request):
    """Registration view for survivors/users"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'survivor'
            user.save()
            messages.success(request, "Account created successfully. You can now log in.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register_user.html', {'form': form})


def register_counselor_view(request):
    """Registration view for counselors"""
    if request.method == 'POST':
        form = CounselorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'counselor'
            user.save()

            # Create counselor profile
            counselor_profile = CounselorProfile(
                user=user,
                license_number=form.cleaned_data['license_number'],
                specialization=form.cleaned_data['specialization'],
                years_of_experience=form.cleaned_data['years_of_experience'],
                is_verified=False  # Pending admin verification
            )
            counselor_profile.save()

            messages.success(request, "Your registration is pending verification by an admin.")
            return redirect('login')
    else:
        form = CounselorRegistrationForm()
    return render(request, 'register_counselor.html', {'form': form})


@login_required
def user_dashboard(request):
    """Dashboard for survivors/users"""
    if request.user.user_type != 'survivor':
        raise PermissionDenied("You don't have permission to access this dashboard.")

    assignments = Assignment.objects.filter(
        survivor=request.user,
        status__in=['active', 'suspended']
    ).select_related('counselor')

    return render(request, 'user_dashboard.html', {'assignments': assignments})


@login_required
def counselor_dashboard(request):
    """Dashboard for counselors"""
    if request.user.user_type != 'counselor':
        raise PermissionDenied("You don't have permission to access this dashboard.")

    if not hasattr(request.user, 'counselorprofile') or not request.user.counselorprofile.is_verified:
        return render(request, 'counselor_pending.html')

    assignments_count = Assignment.objects.filter(
        counselor=request.user,
        status='active'
    ).count()

    return render(request, 'counselor_dashboard.html', {'assignments_count': assignments_count})


@login_required
@user_passes_test(is_admin)
def verify_counselors(request):
    """Admin view to list all counselors pending verification"""
    context = {
        'pending_counselors': CounselorProfile.objects.filter(is_verified=False).select_related('user'),
        'verified_counselors': CounselorProfile.objects.filter(is_verified=True).select_related('user'),
    }
    return render(request, 'verify_counselors.html', context)


@login_required
@user_passes_test(is_admin)
def counselor_verification_detail(request, counselor_id):
    """Admin view to verify a specific counselor"""
    counselor_profile = get_object_or_404(
        CounselorProfile.objects.select_related('user'),
        id=counselor_id
    )

    if request.method == 'POST':
        form = CounselorVerificationForm(request.POST, instance=counselor_profile)
        if form.is_valid():
            profile = form.save()
            verification_status = "verified" if profile.is_verified else "rejected"
            messages.success(
                request,
                f"Counselor {profile.user.username} has been {verification_status}"
            )
            return redirect('verify_counselors')
    else:
        form = CounselorVerificationForm(instance=counselor_profile)

    return render(request, 'counselor_verification_detail.html', {
        'form': form,
        'counselor': counselor_profile.user,
        'profile': counselor_profile
    })


@login_required
@user_passes_test(is_counselor)
def update_counselor_profile(request):
    """View for counselors to update their profile information"""
    profile = get_object_or_404(CounselorProfile, user=request.user)

    if request.method == 'POST':
        form = CounselorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.cleaned_data.pop('confirm_license', None)
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('counselor_dashboard')
    else:
        form = CounselorProfileForm(instance=profile)

    return render(request, 'update_counselor_profile.html', {'form': form})


@login_required
@user_passes_test(is_counselor)
def assignment_list(request):
    """View for counselors to see their assigned survivors"""
    assignments = Assignment.objects.filter(
        counselor=request.user,
        status__in=['active', 'suspended']
    ).select_related('survivor')

    return render(request, 'assignment_list.html', {'assignments': assignments})


@login_required
def assignment_detail(request, assignment_id):
    """View details of a specific counselor-survivor assignment"""
    if request.user.user_type == 'survivor':
        query_params = {'survivor': request.user}
    elif request.user.user_type == 'counselor':
        query_params = {'counselor': request.user}
    else:
        raise PermissionDenied("You don't have permission to view this assignment.")

    assignment = get_object_or_404(
        Assignment.objects.select_related('counselor', 'survivor'),
        id=assignment_id,
        **query_params
    )

    return render(request, 'assignment_detail.html', {'assignment': assignment})


@login_required
@user_passes_test(is_counselor)
@require_http_methods(["POST"])
def update_assignment_notes(request, assignment_id):
    """AJAX view to update assignment notes"""
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid request method'},
            status=400
        )

    assignment = get_object_or_404(
        Assignment,
        counselor=request.user,
        id=assignment_id
    )

    notes = request.POST.get('notes', '').strip()
    assignment.notes = notes
    assignment.save(update_fields=['notes'])

    @login_required
    @user_passes_test(lambda u: u.is_staff)
    def verify_counselors(request):
        """View to list all counselors pending verification"""
        pending_counselors = CounselorProfile.objects.filter(is_verified=False)
        verified_counselors = CounselorProfile.objects.filter(is_verified=True)

        context = {
            'pending_counselors': pending_counselors,
            'verified_counselors': verified_counselors,
        }
        return render(request, 'verify_counselors.html', context)

    @login_required
    @user_passes_test(lambda u: u.is_staff)
    def counselor_verification_detail(request, counselor_id):
        """View to verify or reject a specific counselor"""
        counselor_profile = get_object_or_404(CounselorProfile, id=counselor_id)

        if request.method == 'POST':
            verification_status = request.POST.get('verification_status')

            if verification_status in ['verified', 'rejected']:
                counselor_profile.is_verified = (verification_status == 'verified')
                counselor_profile.save()

                if counselor_profile.is_verified:
                    messages.success(request,
                                     f"Counselor {counselor_profile.user.get_full_name()} has been verified successfully.")
                else:
                    messages.warning(request, f"Counselor {counselor_profile.user.get_full_name()} has been rejected.")

                return redirect('verify_counselors')

        context = {
            'counselor': counselor_profile,
        }
        return render(request, 'counselor_verification_detail.html', context)

    return JsonResponse({'status': 'success', 'message': 'Notes updated successfully'})