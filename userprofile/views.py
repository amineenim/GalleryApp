from datetime import timedelta, date
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import UserProfileCreateForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import html
from django_countries.fields import Country
from friends.models import FriendshipRequest
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
            if len(searched_value) > 0 :
                # we look for matches in both username and email fields 
                searched_value = html.escape(searched_value)
                results = User.objects.filter(Q(username__icontains=searched_value) | Q(email__icontains=searched_value))
                results = results.exclude(username=request.user.username)
                is_a_list = False 
        if is_editing :
            user_profile_data = user_profile_data[0]
            # this means that the user has already filled his data
            form = UserProfileCreateForm(instance=user_profile_data)
            if not(is_a_list) :
                return render(request, 'userprofile/profile.html', {'form' : form, 'is_first_time' : False, 'user_profile_data' : user_profile_data, 'search_results' : results, 'searched_value' : searched_value})
            return render(request, 'userprofile/profile.html', {'form' : form, 'is_first_time' : False, 'user_profile_data' : user_profile_data})
        else :
            form = UserProfileCreateForm()
            if not(is_a_list) :
                return render(request, 'userprofile/profile.html', {'form' : form, 'is_first_time' : True, 'search_results' : results, 'searched_value' : searched_value})
            return render(request, 'userprofile/profile.html', {'form' : form, 'is_first_time' : True})
    

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
                
# view that handles displaying some user profile for the authenticated user 
@login_required
def get_profile(request, username) : 
    # check if the user with the given username exists or not, username is unique 
    try :
        user = User.objects.get(username=username)
    except User.DoesNotExist :
        messages.error(request, 'Not found 404')
        return redirect(reverse('gallery'))
    user_profile_data = UserProfile.objects.filter(user=user)
    # the user may or may not have the profile data , depends if he alredy filled it or not
    context = {}
    # define some variables to store if we're friends or not yet 
    are_we_friends = False 
    i_invited_him = False
    he_invited_me = False 
    no_invitation = True 
    # check if the currently authenticated user has already sent a friendship request to the user with this username
    have_i_already_sent_a_friendship_request = FriendshipRequest.objects.filter(initiated_by=request.user, sent_to=user).exists()
    if have_i_already_sent_a_friendship_request :
        i_invited_him = True 
        no_invitation = False 
        # there's two options, either he accepted the friendship request or not yet 
        if FriendshipRequest.objects.filter(initiated_by=request.user, sent_to=user).first().status == True :
            are_we_friends = True 

    # check if he has already sent a friendship request to the authenticated user 
    has_he_already_sent_a_friendship_request_to_me = FriendshipRequest.objects.filter(initiated_by = user, sent_to=request.user).exists()
    if has_he_already_sent_a_friendship_request_to_me :
        he_invited_me = True 
        no_invitation = False 
        # either i already accepted his request or not yet 
        if FriendshipRequest.objects.filter(initiated_by=user, sent_to=request.user).first().status == True :
            are_we_friends = True 

    if user_profile_data.exists():
        # get data about the country which is stored in 2_alpha
        country = Country(user_profile_data.first().country)
        if country :
            context = {'user_profile_data' : user_profile_data.first(), 'username' : username,
                       'country_data' : country,
                       'are_we_friends' : are_we_friends,
                       'i_invited_him' : i_invited_him,
                       'he_invited_me' : he_invited_me,
                       'no_invitation' : no_invitation}
        else : 
            context = {'user_profile_data' : user_profile_data.first(), 'username' : username,
                       'are_we_friends' : are_we_friends,
                       'i_invited_him' : i_invited_him,
                       'he_invited_me' : he_invited_me,
                       'no_invitation' : no_invitation}
        return render(request, 'userprofile/user_profile.html', context)
    else :
        context = {'username' : username, 'are_we_friends' : are_we_friends, 
                   'i_invited_him' : i_invited_him,
                   'he_invited_me' : he_invited_me,
                   'no_invitation' : no_invitation}
        return render(request, 'userprofile/user_profile.html', context)
    
    
