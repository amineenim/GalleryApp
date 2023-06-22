from datetime import timedelta, date
from django.shortcuts import render, redirect
from .forms import UserProfileCreateForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import html
# Create your views here.
@login_required
def get_my_profile(request) :
    user_profile_data = UserProfile.objects.filter(user=request.user) or None 
    # a variable that stores whether the user is editing or adding data for the first time 
    if user_profile_data :
        is_editing = True
    else :
        is_editing = False  
    # check if it's a get request
    if request.method == 'GET' :
        results = []
        is_a_list = True 
        searched_value = ''
        # check if there is a search param in the URL 
        if 'search' in request.GET :
            searched_value = request.GET.get('search')
            # trim the input value
            searched_value = searched_value.strip()
            searched_value = html.escape(searched_value)
            if len(searched_value) > 0 :
                # we look for matches in both username and email fields 
                results = User.objects.filter(Q(username__icontains=searched_value) | Q(email__icontains=searched_value))
                is_a_list = False 
        if is_editing :
            user_profile_data = user_profile_data[0]
            # this means that the user has already filled his data
            form = UserProfileCreateForm(instance=user_profile_data)
            if not(is_a_list) :
                return render(request, 'userprofile/profile.html', {'form' : form, 'is_first_time' : False, 'user_profile_data' : user_profile_data, 'search_results' : results, 'searched_value' : searched_value})
            return render(request, 'userprofile/profile.html', {'form' : form, 'is_first_time' : False, 'user_profile_data' : user_profile_data, 'searched_value' : searched_value})
        else :
            form = UserProfileCreateForm()
            if not(is_a_list) :
                return render(request, 'userprofile/profile.html', {'form' : form, 'is_first_time' : True, 'search_results' : results, 'searched_value' : searched_value})
            return render(request, 'userprofile/profile.html', {'form' : form, 'is_first_time' : True, 'searched_value' : searched_value})
    

    elif request.method == 'POST' :
        if not(is_editing) :
            form = UserProfileCreateForm(request.POST, request.FILES)
            if form.is_valid() :
                # validate the date 
                if form.cleaned_data['birthdate'] >= date.today() :
                    return render(request, 'userprofile/profile.html', {'form' : form, 'error_birthdate' : 'unvalid birthdate'})
                elif form.cleaned_data['birthdate'] > date.today() - timedelta(days=365*5) or form.cleaned_data['birthdate'] < date.today() - timedelta(days=365*70) :
                    return render(request, 'userprofile/profile.html', {'form' : form,
                                                                        'error_birthdate' : f"unvalid date pick a date between {date.today() - timedelta(days=365*70)} and {date.today() - timedelta(days=365*5)}"})

                new_user_profile_data = form.save(commit=False)
                new_user_profile_data.user = request.user
                new_user_profile_data.save()
                messages.success(request, 'Profile data added with success')
            return redirect('profile:my_profile')
        else :
            form = UserProfileCreateForm(request.POST, request.FILES, instance=user_profile_data.first())
            if form.is_valid() :
                # validate the date 
                if form.cleaned_data['birthdate'] >= date.today() :
                    return render(request, 'userprofile/profile.html', {'form' : form, 'error_birthdate' : 'unvalid birthdate'})
                elif form.cleaned_data['birthdate'] > date.today() - timedelta(days=365*5) or form.cleaned_data['birthdate'] < date.today() - timedelta(days=365*70) :
                    return render(request, 'userprofile/profile.html', {'form' : form,
                                                                        'error_birthdate' : f"unvalid date pick a date between {date.today() - timedelta(days=365*70)} and {date.today() - timedelta(days=365*5)}"})

                form.save()
                messages.success(request, 'profile data modified succesefully')
            return redirect('profile:my_profile')
                
    
