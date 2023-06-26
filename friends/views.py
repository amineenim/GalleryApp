from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from .models import FriendshipRequest, FriendshipNotification, FriendsList
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
        friendshp_request, created = FriendshipRequest.objects.get_or_create(initiated_by = request.user, sent_to = user_to_receive_request )
        if created :
            # create the corresponding notification
            FriendshipNotification.objects.create(intended_to=user_to_receive_request,
                                                  content = f"{request.user.username} sent you a friendship request")
            messages.success(request, f"Friendship request sent successefully to {username}")
            return redirect(reverse('profile:view_profile', args=(username,)))
        else : 
            # if the request already exists the user can delete it, in other words he cancels the friendship request he already sent
            friendshp_request.delete()
            # delete the corresponding notification 
            corresponding_notification = FriendshipNotification.objects.filter(intended_to = user_to_receive_request,
                                                                               content=f"{request.user.username} sent you a friendship request").first()
            corresponding_notification.delete()
            messages.success(request, f"Your Freindship request to {username} has been canceled")
            return redirect(reverse('profile:view_profile', args=(username,)))
        

@login_required
def get_notifications(request) :
    # get all notifications for the authenticated user 
    notifications = request.user.my_friendship_notifications.all()
    unseen_notifications = request.user.my_friendship_notifications.filter(is_seen=False)
    if unseen_notifications.exists() :
        for notif in unseen_notifications :
            notif.is_seen = True 
            notif.save()
        return render(request, 'friends/notifications.html', {'all_notifications' : notifications})
    return render(request, 'friends/notifications.html', {'all_notifications' : notifications})


@login_required
def accept_friendship_request(request, username) :
    if request.method == 'POST' :
        # check for the user with username
        try : 
            friendship_request_sender = User.objects.get(username=username)
        except User.DoesNotExist :
            return redirect('gallery')
        # add the friend to the list of friends and generate a notification, set status of friendship request to true
        friendship_request = FriendshipRequest.objects.filter(initiated_by=friendship_request_sender, sent_to=request.user).first()
        friendship_request.status = True
        friendship_request.save()
        my_friends, created = FriendsList.objects.get_or_create(belongs_to=request.user)
        my_friends.friends.add(friendship_request_sender)
        FriendshipNotification.objects.create(intended_to=friendship_request_sender, content=f"{request.user.username} accepted your friendship request")
        messages.success(request, f"You and {username} are friends now")

    return redirect(reverse('profile:view_profile', args=(username,)))



