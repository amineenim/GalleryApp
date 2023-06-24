from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from .models import FriendshipRequest
from django.contrib import messages
# Create your views here.

# view that handles sending a friendship request to someone
@login_required
def send_friendship_request(request, username) :
    # the username variable received refers to the user receiving the friendship_request
    if request.method == 'POST' :
        # check if the user with the given username exists or not 
        try :
            user_to_receive_request = User.objects.get(username=username)
        except User.DoesNotExist :
            return redirect(reverse('gallery'))
        # create a FriedshipRequest Object if it doesn't already exist
        friendshp_request, created = FriendshipRequest.objects.get_or_create(
            {'initiated_by' : request.user, 'sent_to' : user_to_receive_request }
        )
        if created :
            messages.success(request, f"Friendship request sent successefully to {username}")
            return redirect(reverse('profile:view_profile', args=(username,)))
        else : 
            # if the request already exists the user can delete it, in other words he cancels the friendship request he already sent
            friendshp_request.delete()
            messages.success(request, f"Your Freindship request to {username} has been canceled")
            return redirect(reverse('profile:view_profile', args=(username,)))
        




