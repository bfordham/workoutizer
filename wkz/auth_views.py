from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import Http404

from .auth_forms import SignUpForm, UserProfileEditForm, UserProfileSettingsForm
from .models import get_user_profile, Activity


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
    profile = get_user_profile(request.user)
    
    if request.method == 'POST':
        user_form = UserProfileEditForm(request.POST, instance=request.user)
        settings_form = UserProfileSettingsForm(request.POST, instance=profile)
        
        if user_form.is_valid() and settings_form.is_valid():
            user_form.save()
            settings_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserProfileEditForm(instance=request.user)
        settings_form = UserProfileSettingsForm(instance=profile)
    
    return render(request, 'auth/edit_profile.html', {
        'user_form': user_form,
        'settings_form': settings_form
    })


def public_profile_view(request, username):
    """Public profile view that shows user's activities if they have enabled public profile"""
    user = get_object_or_404(User, username=username)
    profile = get_user_profile(user)
    
    # Check if profile is public
    if not profile.public_profile:
        raise Http404("Profile not found")
    
    # Get user's activities (recent 50)
    activities = Activity.objects.filter(user=user).order_by('-date')[:50]
    
    # Calculate basic stats
    total_activities = Activity.objects.filter(user=user).count()
    total_distance = sum(activity.distance or 0 for activity in Activity.objects.filter(user=user))
    
    context = {
        'profile_user': user,
        'profile': profile,
        'activities': activities,
        'total_activities': total_activities,
        'total_distance': round(total_distance, 2),
        'page_name': f"{user.get_full_name() or user.username}'s Profile"
    }
    
    return render(request, 'auth/public_profile.html', context)