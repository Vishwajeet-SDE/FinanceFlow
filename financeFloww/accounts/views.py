from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import CustomUserCreationForm, UserProfileForm, UserUpdateForm
from .models import UserProfile
from django.db import transaction as db_transaction
from django.contrib.auth.models import User


def home(request):
    """Home page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')


@require_http_methods(["GET", "POST"])
def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with db_transaction.atomic():
                user = form.save()
                # Create user profile
                UserProfile.objects.create(user=user)
                
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


@login_required
@require_http_methods(["GET"])
def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    """User profile view"""
    try:
        user_profile = request.user.profile
    
    except:
        # Create profile if it doesn't exist
        from .models import UserProfile
        user_profile = UserProfile.objects.create(user=request.user)
        
    context = {
        'user_profile': user_profile,
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    """Edit user profile"""
    user_profile = request.user.profile

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        user_form = UserUpdateForm(request.POST, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            with db_transaction.atomic():
                profile_form.save()
                user_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=user_profile)
        user_form = UserUpdateForm(instance=request.user)

    context = {
        'profile_form': profile_form,
        'user_form': user_form,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def settings(request):
    """User settings"""
    user_profile = request.user.profile
    
    context = {
        'user_profile': user_profile,
        'user': request.user,
    }
    return render(request, 'accounts/settings.html', context)