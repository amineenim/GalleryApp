from django.shortcuts import render

# Create your views here.
def get_my_profile(request) :
    return render(request, 'userprofile/profile.html', {})
