from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .auth_forms import SignUpForm, UserProfileEditForm
from .models import get_user_profile


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            get_user_profile(user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})


@login_required
def profile_view(request):
    profile = get_user_profile(request.user)
    return render(request, 'auth/profile.html', {'profile': profile})


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileEditForm(instance=request.user)
    
    return render(request, 'auth/edit_profile.html', {'form': form})