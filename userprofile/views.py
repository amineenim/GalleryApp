from django.shortcuts import render
from .forms import UserProfileCreateForm
# Create your views here.
def get_my_profile(request) :
    form = UserProfileCreateForm()
    return render(request, 'userprofile/profile.html', {'form' : form})
