from datetime import datetime, timedelta, date
from django.shortcuts import render, redirect
from .forms import UserProfileCreateForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.
@login_required
def get_my_profile(request) :
    # check if it's a get request
    if request.method == 'GET' :
        user_profile_data = UserProfile.objects.filter(user=request.user)
        if user_profile_data.exists() :
            # this means that the user has already filled his data
            user_profile_data = user_profile_data[0]
            form = UserProfileCreateForm(instance=user_profile_data)
            if user_profile_data.profile_picture :
                profile_picture = user_profile_data.profile_picture
                return render(request, 'userprofile/profile.html', {'form' : form, 'is_first_time' : False, 'profile_picture' : profile_picture})
            return render(request, 'userprofile/profile.html', {'form' : form, 'is_first_time' : False})
        else :
            form = UserProfileCreateForm()
            return render(request, 'userprofile/profile.html', {'form' : form, 'is_first_time' : True})
    
    elif request.method == 'POST' :
        
        form = UserProfileCreateForm(request.POST, request.FILES)
        if form.is_valid() :
            # validate the date 
            if form.cleaned_data['birthdate'] >= date.today() :
                return render(request, 'userprofile/profile.html', {'form' : form, 'error_birthdate' : 'unvalid birthdate'})
            elif form.cleaned_data['birthdate'] > date.today() - timedelta(days=365*5) or form.cleaned_data['birthdate'] < date.today() - timedelta(days=365*70) :
                return render(request, 'userprofile/profile.html', {'form' : form,
                                                                     'error_birthdate' : f"unvalid date pick a date between {date.today() - timedelta(days=365*70)} and {date.today() - timedelta(days=365*5)}"})
            else :
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                birthdate = form.cleaned_data['birthdate']
                bio = form.cleaned_data['bio']
                profile_picture = form.cleaned_data['profile_picture']
                country = form.cleaned_data['country']
                user_profile_data = UserProfile.objects.create(
                    first_name=first_name,
                    last_name = last_name,
                    birthdate = birthdate,
                    bio = bio,
                    user = request.user,
                    profile_picture = profile_picture,
                    country = country
                )
                if user_profile_data : 
                    messages.success(request, 'Profile data added successefully')
                    return redirect('profile:my_profile')
                
        return render(request, 'userprofile/profile.html',{'form' : form})
    
