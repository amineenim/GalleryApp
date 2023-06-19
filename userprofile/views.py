from django.shortcuts import render
from .forms import UserProfileCreateForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def get_my_profile(request) :
    print('method is get')
    # check if it's a get request
    if request.method == 'GET' :
        user_profile_data = UserProfile.objects.filter(user=request.user)
        if user_profile_data.exists() :
            # this means that the user has already filled his data
            user_profile_data = user_profile_data[0]
            form = UserProfileCreateForm(instance=user_profile_data)
            return render(request, 'userprofile/profile.html', {'form' : form, 'is_first_time' : False})
        else :
            form = UserProfileCreateForm()
            return render(request, 'userprofile/profile.html', {'form' : form, 'is_first_time' : True})
    
    elif request.method == 'POST' :
        print('post method')
        print(request.POST)
        print(request.POST.get('birthdate'))
        print(type(request.POST.get('birthdate')))
        form = UserProfileCreateForm(request.POST, request.FILES)
        if form.is_valid() :
            print(form.cleaned_data)
        else :
            print(form.errors)
        return render(request, 'userprofile/profile.html',{'form' : form})
