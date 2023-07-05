from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from .models import FriendshipRequest, FriendshipNotification, FriendsList, Conversation, ConversationMessage
from django.contrib import messages
from django.utils.html import escape
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
        my_friends.save()
        # same thing for user with 'username'
        username_friends, created = FriendsList.objects.get_or_create(belongs_to=friendship_request_sender)
        username_friends.friends.add(request.user)
        username_friends.save()
        FriendshipNotification.objects.create(intended_to=friendship_request_sender, content=f"{request.user.username} accepted your friendship request")
        messages.success(request, f"You and {username} are friends now")

    return redirect(reverse('profile:view_profile', args=(username,)))

@login_required 
def decline_friendship_request(request, username) :
    # this function handles declining a friendship request , it must delete
    # the FriendshipRequest object, and the corresponding FriendshipNotification Object also 
    if request.method == 'POST' :
        # check if the user exists or not 
        try :
            request_sender = User.objects.get(username=username)
        except User.DoesNotExist :
            messages.error(request, 'Oops, something went wrong !')
            return redirect(reverse('gallery'))
        # delete the FriendshipRequest Object 
        friendship_request_to_delete = FriendshipRequest.objects.filter(initiated_by=request_sender, sent_to=request.user, status=False).first()
        friendship_request_to_delete.delete()
        # get the corresponding Notification that was sent to the receiver of the request
        # since the request has been canceled 
        friendship_notification_to_delete = FriendshipNotification.objects.filter(intended_to=request.user, content=f"{request_sender.username} sent you a friendship request").first()
        friendship_notification_to_delete.delete()
        messages.success(request, 'Friendship request declined successefully !')
    return redirect(reverse('profile:view_profile', args=(username,)))

@login_required 
def get_list_of_my_friends(request) :
    friends_list, created = FriendsList.objects.get_or_create(belongs_to=request.user)
    friends = friends_list.friends.all()
    # create a session variable to store opened conversations 
    conversations = request.session.get('conversations')
    deserialized_conversations = []
    if conversations is None :
        conversations = []
        request.session['conversations'] = conversations
    else :
        # deserialize conversations 
        for conv in conversations :
            deserialized_conversation = Conversation.from_json(conv)
            deserialized_conversations.append(deserialized_conversation)

    if request.method == 'GET' :
        if 'conversations' in request.session :
            return render(request, 'friends/my_friends.html', {'friends' : friends, 'friends_list' : friends_list, 'conversations' : deserialized_conversations})
            #del request.session['conversations']
        return render(request, 'friends/my_friends.html', {'friends' : friends, 'friends_list' : friends_list})
    elif request.method == 'POST' :
        # get the username value submitted 
        username = request.POST.get('username')
        user = User.objects.get(username=username)
        # create a conversation object if it already doesn't exist 
        if Conversation.objects.filter(member_one=request.user, member_two=user).exists() or Conversation.objects.filter(member_one=user, member_two=request.user).exists() :
            # get the corresponding Conversation object
            conversation = Conversation.objects.filter(member_one=request.user, member_two=user) or Conversation.objects.filter(member_one=user, member_two=request.user)
            # serialize the conversation object and store it in session
            serialized_conversation = conversation[0].to_json()
            # check if the conversation doesn't already exist in opened conversations 
            if serialized_conversation not in request.session['conversations'] :
                conversations.append(serialized_conversation)
                deserialized_conversation = Conversation.from_json(serialized_conversation)
                deserialized_conversations.append(deserialized_conversation)
                request.session['conversations'] = conversations
            
            return render(request, 'friends/my_friends.html', 
                          {'friends' : friends, 'friends_list' : friends_list, 'conversations' : deserialized_conversations})
        else :
            # create the conversation object 
            conversation = Conversation.objects.create(member_one=request.user, member_two=user)
            # serialize and store it in session 
            serialized_conversation = conversation.to_json()
            # check if the conversation is already in opened conversations 
            if serialized_conversation not in request.session['conversations'] :
                # store in session
                conversations.append(serialized_conversation)
                deserialized_conversation = Conversation.from_json(serialized_conversation)
                deserialized_conversations.append(deserialized_conversation)
                request.session['conversations'] = conversations
            return render(request, 'friends/my_friends.html', 
                          {'friends' : friends, 'friends_list' : friends_list, 'conversations' : deserialized_conversations})
        

@login_required
def close_conversation(request) :
    username = request.POST.get('username')
    if request.method == 'POST' :
        # check for username 
        try :
            user = User.objects.get(username=username)
        except User.DoesNotExist :
            messages.error(request,'Oops ! something went wrong')
            return redirect(reverse('friends:my_friends'))
        # check for session data which holds opened conversations and delete the one with the user having username
        session_data = request.session.get('conversations')
        if session_data is None :
            # no key 'conversations' was found in session data 
            return redirect(reverse('friends:my_friends'))
        # get the conversation object between authenticated user and username
        conversation = Conversation.objects.filter(member_one=request.user, member_two=user).first() or Conversation.objects.filter(member_one=user, member_two=request.user).first()
        # serialize the conversation instance
        serialized_conv = conversation.to_json()
        # filter session data 
        session_data = [conv for conv in session_data if conv != serialized_conv]
        request.session['conversations'] = session_data
        return redirect(reverse('friends:my_friends'))

@login_required 
def send_message(request, username) :
    # get the user with 'username'
    try :
        user = User.objects.get(username=username)
    except User.DoesNotExist :
        messages.error(request, 'Oops, something went wrong !')
        return redirect('friends:my_friends')
    # check if user is on the authenticated user's friends_list 
    try :
        friends_list = FriendsList.objects.get(belongs_to = request.user)
    except FriendsList.DoesNotExist :
        messages.error(request, 'something went wrong!, no friends to text')
        return redirect('friends:my_friends')
    if user not in friends_list.friends.all() :
        messages.error(request, 'unauthorized action, you are not friends!')
        return redirect('friends:my_friends')
    # check for post request 
    if request.method == 'POST' :
        # get the conversation object 
        try :
            conversation = Conversation.objects.get(member_one=request.user, member_two=user)         
        except Conversation.DoesNotExist :
            try :
                conversation = Conversation.objects.get(member_one=user, member_two=request.user)
            except Conversation.DoesNotExist :
                messages.error(request, 'something went wrong !')
                return redirect('friends:my_friends')
        # validate the input received from the form 
        text_message = request.POST.get('message')
        if text_message and text_message.strip() :
            text_message = escape(text_message)
            # create the message object
            message = ConversationMessage.objects.create(
                conversation=conversation,
                text = text_message,
                sent_by = request.user,
            )
            message.save()
        else :
            messages.error(request, 'invalid message, Enter some text')
            
        return redirect('friends:my_friends')
    else :
        messages.error(request, 'undefined URL !')
        return redirect('gallery')

# function that handles displaying messages notifications 
@login_required
def get_messages_notifications(request) :
    pass 