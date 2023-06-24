from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.

# view that handles sending a friendship request to someone
@login_required
def send_friendship_request(request) :
    return render(request, 'friends/base.html', {})

