from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from .models import FriendshipRequest, FriendshipNotification
# Create your tests here.

# class to test the operation of the send_friendship_request View 
class SendFriendshipRequestViewTests(TestCase) :
    # test send_friendship_request with unauthenticated user 
    def test_send_friendship_request_with_unauthenticated_user(self) :
        # i pass a username which doesn't exist but it doesn't matter the user is unauthenticated
        target_url = reverse('friends:send_request', args=('test',))
        response = self.client.post(target_url,{})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")

    # test send_friendship_request to a user who does not exist 
    def test_send_friendship_request_to_unexisting_user(self) :
        # create a user and autneticate him 
        User.objects.create_user(username='amine', password='test')
        self.client.login(username='amine', password='test')
        # i pass as a username argument 'not_existing' which doesn't refer to any user
        target_url = reverse('friends:send_request', args=('not_existing',))
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
    
    # test send_friendship_request to a user , with no previous friendship request already sent to him by the authenticated user
    def test_send_friendship_request_to_user_with_no_previous_friendship_request_from_authenticated_user(self) :
        User.objects.create_user(username='receiver', password='1234')
        # create a user and authenticate him
        User.objects.create_user(username='amine', password='test')
        self.client.login(username='amine', password='test')
        # check the "receiver" profile to see if he has "add as a friend"
        profile_url = reverse('profile:view_profile', args=('receiver',))
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['username'], 'receiver')
        self.assertEqual(response.context['are_we_friends'], False)
        self.assertEqual(response.context['no_invitation'], True)
        self.assertContains(response, 'Add as a Friend')
        # pass 'receiver' as the username param value
        target_url = reverse('friends:send_request', args=('receiver',))
        response = self.client.post(target_url, {})
        # check response status
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile:view_profile', args=('receiver',)))
        # check messages 
        my_messages = list(messages.get_messages(response.wsgi_request))
        for message in my_messages :
            self.assertEqual(message.tags, 'success')
            self.assertEqual(message.message, 'Friendship request sent successefully to receiver')
        # check that  FriendshipRequest object has been created 
        self.assertTrue(FriendshipRequest.objects.exists())
        # now after the request has been sent, verify "receiver" profile again
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['are_we_friends'], False)
        self.assertEqual(response.context['i_invited_him'], True)
        self.assertEqual(response.context['no_invitation'], False)
        self.assertContains(response, 'Cancel my Request')        
    
    # test send_friendship request to a user to whom i've already sent a friendship request 
    def test_send_friendship_request_to_user_to_whom_i_already_sent_one(self) :
        # create the user to whom send the request 
        user_to_receive_request = User.objects.create_user(username='receiver', password='test')
        # create a user and authenticate him
        sender = User.objects.create_user(username='sender', password='1234')
        self.client.login(username='sender', password='1234')
        # create a FriendshipRequest object 
        FriendshipRequest.objects.create(
            initiated_by = sender,
            sent_to = user_to_receive_request,
        )
        # since now the request has been already sent, when going to the receiver profile the sender can not send once again
        target_url = reverse('profile:view_profile', args=('receiver',))
        response = self.client.get(target_url)
        # check the response status and data 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['username'], 'receiver')
        self.assertEqual(response.context['are_we_friends'], False)
        self.assertEqual(response.context['he_invited_me'], False)
        self.assertEqual(response.context['i_invited_him'], True)
        self.assertEqual(response.context['no_invitation'], False)
        #check that the user can only cancel the request he already sent 
        self.assertContains(response, 'Cancel my Request')
        # try to cancel the request 
        response = self.client.post(reverse('friends:send_request',args=('receiver',)), {})
        # now that the request has been deleted , check that there are no FriendshipRequest objects
        self.assertFalse(FriendshipRequest.objects.exists())
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'success')
            self.assertEqual(message.message, 'Your Freindship request to receiver has been canceled')
        self.assertEqual(response.status_code, 302)
        # check that we will redirect to the receiver profile again
        self.assertRedirects(response, target_url)
        # now that the friendship request has been canceled, get the receiver profile again
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['no_invitation'], True)
        self.assertContains(response, 'Add as a Friend')
    
    # test send_friendship_request to a user who already sent me one 
    def test_send_friendship_request_to_a_user_who_already_sent_me_one(self) :
        # create the receiver user 
        user_to_receive_friendship_request = User.objects.create_user(username='receiver', password='receiver')
        # create the user who will send a friendship request to 'receiver'
        sender = User.objects.create_user(username='sender', password='sender')
        # create the FriendshipRequest Object 
        FriendshipRequest.objects.create(initiated_by=sender, sent_to=user_to_receive_friendship_request)
        # authenticate the receiver
        self.client.login(username='receiver', password='receiver')
        # check the sender profile 
        target_url = reverse('profile:view_profile', args=('sender',))
        response = self.client.get(target_url)
        # check response status and data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['no_invitation'], False)
        self.assertEqual(response.context['are_we_friends'], False)
        self.assertEqual(response.context['i_invited_him'], False)
        self.assertEqual(response.context['he_invited_me'], True)
        self.assertEqual(response.context['username'], 'sender')
        self.assertContains(response, 'Accept')
        self.assertContains(response, 'Decline')

# class to test the operation of get_notifications view
class GetNotificationsViewTests(TestCase) :
    # test get_notifications view with an unauthenticated user 
    def test_get_friendship_notifications_with_unauthenticated_user(self) :
        target_url = reverse('friends:notifications')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
    
    # test get_notifications view with a user who sends a friendship request to other user 
    def test_get_notifications_with_user_who_receives_a_friendship_request_from_other_user(self) :
        # create two users, the sender of friendship request and the receiver
        sender = User.objects.create_user(username='sender', password='sender')
        receiver = User.objects.create_user(username='receiver', password='receiver')
        # authenticate the sender and send a friendship request to 'receiver'
        self.client.login(username='sender', password='sender')
        # pass 'receiver' as the username argument to the url
        target_url = reverse('friends:send_request', args=('receiver',))
        # send the post request 
        response = self.client.post(target_url, {})
        #check the response status and data 
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile:view_profile', args=('receiver',)))
        # check that a FriendshipRequest object has been created 
        self.assertTrue(FriendshipRequest.objects.exists())
        self.assertEqual(FriendshipRequest.objects.first().status, False)
        self.assertEqual(FriendshipRequest.objects.first().initiated_by, sender)
        self.assertEqual(FriendshipRequest.objects.first().sent_to, receiver)
        # check that a FriendshipNotification Object has been created 
        self.assertTrue(FriendshipNotification.objects.exists())
        # go to the profile of 'receiver'
        response = self.client.get(reverse('profile:view_profile', args=('receiver',)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['are_we_friends'], False)
        self.assertEqual(response.context['no_invitation'], False)
        self.assertEqual(response.context['i_invited_him'], True)
        self.assertEqual(response.context['he_invited_me'], False)
        self.assertContains(response, 'Cancel my Request')
        # logout 'sender' and authenticate 'receiver'
        self.client.logout()
        self.client.login(username='receiver', password='receiver')
        # go to home page and check that the receiver has one unread notification 
        response = self.client.get(reverse('gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['friendship_notifications'], FriendshipNotification.objects.all())
        self.assertEqual(FriendshipNotification.objects.first().is_seen, False)
        # check that the view displays one unread notification
        self.assertContains(response, 1)
        # receiver checks the notifications
        response = self.client.get(reverse('friends:notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context['all_notifications'], FriendshipNotification.objects.filter(intended_to=receiver))
        # check that there's no unseen notification
        self.assertFalse(FriendshipNotification.objects.filter(is_seen=False).exists())
        self.assertContains(response, 'sender sent you a friendship request')
    
    # test get_notifications with a user who cancels an already sent friendship request to other user
    def test_get_notifications_with_user_canceling_friendship_request_to_other_user(self) :
        # create a sender and a receiver users
        sender = User.objects.create_user(username='sender', password='sender')
        receiver = User.objects.create_user(username='receiver', password='receiver')
        # authenticate 'sender' and send a friendship request
        self.client.login(username='sender', password='sender')
        target_url = reverse('friends:send_request', args=('receiver',))
        self.client.post(target_url, {})
        # logout the sender and authenticate receiver 
        self.client.logout()
        self.client.login(username='receiver', password='receiver')
        # check for friendship notifications
        response = self.client.get(reverse('gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['friendship_notifications'], FriendshipNotification.objects.filter(is_seen=False, intended_to=receiver, content='sender sent you a friendship request'))
        self.assertEqual(len(response.context['friendship_notifications']), 1)
        self.assertTrue(FriendshipNotification.objects.exists())
        self.assertContains(response, 1)
        self.assertEqual(len(response.context['friendship_notifications']), 1)
        # logout the receiver and login the sender 
        self.client.logout()
        self.client.login(username='sender', password='sender')
        # check the receiver profile 
        response = self.client.get(reverse('profile:view_profile', args=('receiver',)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['no_invitation'], False)
        self.assertEqual(response.context['i_invited_him'], True)
        self.assertEqual(response.context['he_invited_me'], False)
        self.assertEqual(response.context['are_we_friends'], False)
        self.assertContains(response, 'Cancel my Request')
        # cancel the request 
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile:view_profile', args=('receiver',)))
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'success')
            self.assertEqual(message.message, 'Your Freindship request to receiver has been canceled')
        # logout sender and login receiver 
        self.client.logout()
        self.client.login(username='receiver', password='receiver')
        response = self.client.get(reverse('gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['friendship_notifications'], [])
        self.assertFalse(FriendshipNotification.objects.exists())








