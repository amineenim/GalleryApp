from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from .models import FriendshipRequest, FriendshipNotification, FriendsList, Conversation
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

# class to test the operation of accept_friendship_request View 
class AcceptFriendshipRequestViewTests(TestCase) :
    # test accept_friendship_request View with unauthenticated user 
    def test_accept_friendship_request_with_unauthenticated_user(self):
        target_url = reverse('friends:accept_request', args=('test',))
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
    
    # test accept_friendship_request with unexisting user 
    def test_accept_friendship_request_with_unexisting_user(self) :
        User.objects.create_user(username='amine', password='amine')
        self.client.login(username='amine', password='amine')
        # no user with does_not_exist username exists
        target_url = reverse('friends:accept_request', args=('does_not_exist',))
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
    
    # test accept_friendship_request with user who got a friendship request from other user 
    def test_accept_friendship_request_from_user_who_already_sent_one(self) :
        # create 'sender' and 'receiver'
        sender = User.objects.create_user(username='sender', password='sender')
        receiver = User.objects.create_user(username='receiver', password='receiver')
        # authenticate the sender 
        self.client.login(username='sender', password='sender')
        # send a friendship request to 'receiver'
        target_url = reverse('friends:send_request', args=('receiver',))
        response = self.client.post(target_url, {})
        # check response status and data 
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile:view_profile', args=('receiver',)))
        # check that a FriendshipRequest object has been created 
        self.assertTrue(FriendshipRequest.objects.exists())
        self.assertEqual(FriendshipRequest.objects.first().initiated_by, sender)
        self.assertEqual(FriendshipRequest.objects.first().sent_to, receiver)
        self.assertEqual(FriendshipRequest.objects.first().status, False)
        # check receiver profile 
        response = self.client.get(reverse('profile:view_profile', args=('receiver',)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['username'], 'receiver')
        self.assertEqual(response.context['are_we_friends'], False)
        self.assertEqual(response.context['i_invited_him'], True)
        self.assertEqual(response.context['no_invitation'], False)
        self.assertContains(response, 'Cancel my Request')
        # now that the request has been sent, authenticate receiver and check notifications
        self.client.logout()
        self.client.login(username='receiver', password='receiver')
        # go to home page and check for notifications
        response = self.client.get(reverse('gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(FriendshipNotification.objects.exists())
        self.assertCountEqual(response.context['friendship_notifications'], FriendshipNotification.objects.filter(intended_to=receiver, is_seen=False))
        self.assertEqual(len(response.context['friendship_notifications']), 1)
        # check notifications page 
        response = self.client.get(reverse('friends:notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['all_notifications']), 1)
        self.assertTrue(FriendshipNotification.objects.exists())
        self.assertQuerysetEqual(FriendshipNotification.objects.filter(intended_to=receiver, is_seen=False), [])
        # go to the sender profile 
        response = self.client.get(reverse('profile:view_profile', args=('sender',)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['are_we_friends'], False)
        self.assertEqual(response.context['i_invited_him'], False)
        self.assertEqual(response.context['he_invited_me'], True)
        self.assertEqual(response.context['no_invitation'], False)
        self.assertContains(response, 'Accept')
        self.assertContains(response, 'Decline')
        # accept the friendship request 
        response = self.client.post(reverse('friends:accept_request', args=('sender',)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile:view_profile', args=('sender',)))
        # check that FriendshipRequest object status is now True
        self.assertEqual(FriendshipRequest.objects.first().status, True)
        self.assertEqual(len(FriendshipRequest.objects.all()), 1)
        # check that a FriendsList object has been created 
        self.assertTrue(FriendsList.objects.exists())
        self.assertEqual(FriendsList.objects.first().belongs_to, receiver)

        #self.assertEqual(FriendsList.objects.first().friends, [sender])
        
        self.assertEqual(FriendsList.objects.filter(belongs_to=receiver).first().get_number_of_friends(), 1)
        # check that a notification has been created 
        self.assertTrue(FriendshipNotification.objects.filter(intended_to=sender, content='receiver accepted your friendship request' ).exists())
        # check messages 
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'success')
            self.assertEqual(message.message, "You and sender are friends now")
        # check the sender profile again 
        response = self.client.get(reverse('profile:view_profile', args=('sender',)))
        self.assertContains(response, 'Message')
        self.assertEqual(response.context['are_we_friends'], True)

# class to test the operation of decline_frienship_request View 
class DeclineFriendshipRequestViewTests(TestCase) :
    # test with unauthenticated user 
    def test_decline_request_with_unauthenticated_user(self) :
        target_url = reverse('friends:decline_request', args=('test',))
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
    
    # test decline_friendship_request with unexisting user 
    def test_decline_request_fron_unexisting_user(self) :
        # pass 'test' as the user's username, it doesn't exist
        target_url = reverse('friends:decline_request', args=('test',))
        # create a user and authneticate him
        User.objects.create_user(username='amine', password='1234')
        self.client.login(username='amine', password='1234')
        # send a post request to the url to decline the friendship_request
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        # check messages 
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'error')
            self.assertEqual(message.message, 'Oops, something went wrong !')
    
    # test decline_friendship_request received from an other user 
    def test_decline_request_received_from_other_user(self) :
        # create a sender and a receiver 
        sender = User.objects.create_user(username='sender', password='sender')
        receiver = User.objects.create_user(username='receiver', password='receiver')
        # authenticate sender and check the receiver profile 
        self.client.login(username='sender', password='sender')
        target_url = reverse('profile:view_profile', args=('receiver',))
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['username'], 'receiver')
        self.assertEqual(response.context['are_we_friends'], False)
        self.assertEqual(response.context['no_invitation'], True)
        self.assertContains(response, 'Add as a Friend')
        # send a friendship request to 'receiver'
        target_url = reverse('friends:send_request', args=('receiver',))
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile:view_profile', args=('receiver',)))
        # check that a FriendshipRequest and FriendshipNotification Objects have been created
        self.assertTrue(FriendshipRequest.objects.exists())
        self.assertTrue(FriendshipNotification.objects.exists())
        self.assertEqual(len(FriendshipRequest.objects.all()), 1)
        self.assertEqual(len(FriendshipNotification.objects.all()), 1)
        self.assertTrue(FriendshipRequest.objects.filter(initiated_by=sender, sent_to=receiver, status=False).exists())
        self.assertTrue(FriendshipNotification.objects.filter(intended_to=receiver, content='sender sent you a friendship request').exists())
        # logout the sender and authenticate receiver
        self.client.logout()
        self.client.login(username='receiver', password='receiver')
        # check the home page for notifications
        target_url = reverse('gallery')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['friendship_notifications']), 1)
        self.assertCountEqual(response.context['friendship_notifications'], FriendshipNotification.objects.filter(intended_to=receiver, is_seen=False, content='sender sent you a friendship request'))
        # check notifications page 
        target_url = reverse('friends:notifications')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context['all_notifications'], FriendshipNotification.objects.filter(intended_to=receiver, content='sender sent you a friendship request'))
        self.assertContains(response, 'sender sent you a friendship request')
        # check there are no unseen notifications
        self.assertFalse(FriendshipNotification.objects.filter(is_seen=False).exists())
        # go to the sender profile
        target_url = reverse('profile:view_profile', args=('sender',))
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['username'], 'sender')
        self.assertEqual(response.context['are_we_friends'], False)
        self.assertEqual(response.context['he_invited_me'], True)
        self.assertEqual(response.context['no_invitation'], False)
        self.assertContains(response, 'Accept')
        self.assertContains(response, 'Decline')
        # decline the friendship request 
        target_url = reverse('friends:decline_request', args=('sender',))
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile:view_profile', args=('sender',)))
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for msg in my_messages :
            self.assertEqual(msg.tags, 'success')
            self.assertEqual(msg.message, 'Friendship request declined successefully !')
        # check that there are no more FriendshipRequest or FriendshipNotification Objects
        self.assertFalse(FriendshipRequest.objects.exists())
        self.assertFalse(FriendshipRequest.objects.filter(initiated_by=sender, sent_to=receiver).exists())
        self.assertFalse(FriendshipNotification.objects.filter(intended_to=receiver, content='sender sent you a friendship request').exists())
        self.assertFalse(FriendshipNotification.objects.exists())
        # go to notifications page 
        response = self.client.get(reverse('friends:notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['all_notifications'], [])
        self.assertContains(response, 'No notifications for the moment')

# class to test the operation of since_when method on FriendshipNotification Model 
class SinceWhenFriendshipNotificationTests(TestCase) :
    # function that creates and returns a user 
    def get_user(self) :
        return User.objects.create_user(username='test', password='test123')
    # function that creates a notification a given time ago 
    def create_notification(self, seconds_ago) :
        # create a datetime value before seconds_ago seconds 
        created_at = timezone.now() - timedelta(seconds=seconds_ago)
        notification = FriendshipNotification.objects.create(
            intended_to = self.get_user(),
            content = 'this is a test',
            created_at = created_at
        )
        return notification
    # test since_when method for a FriendshipRequest created in last minute 
    def test_since_when_with_record_created_less_than_a_minute_ago(self) :
        # create a Friendship Notification 
        notification_in_the_last_minute = self.create_notification(40)
        self.assertEqual(notification_in_the_last_minute.since_when(), 'a few moments ago')

    # test since when with a Friendship Request created before 59 seconds
    def test_since_when_with_record_created_before_59_seconds(self) :
        notification_before_59_seconds = self.create_notification(59)
        self.assertEqual(notification_before_59_seconds.since_when(), 'a few moments ago')
    
    # test since when with a friendship request created 1 minute and 1 second ago
    def test_since_when_with_record_created_before_61_seconds(self) :
        notification_before_a_minute_and_one_second = self.create_notification(61)
        self.assertEqual(notification_before_a_minute_and_one_second.since_when(), '1 minutes ago')
    
    # test since when with a record created 59 minutes and 59 seconds ago 
    def test_since_when_with_record_created_one_hour_minus_one_second_ago(self) :
        seconds_ago = 59*60 + 59
        notification = self.create_notification(seconds_ago=seconds_ago)
        self.assertEqual(notification.since_when(), '59 minutes ago')
     
    # test since_when with a record created 1 hour and 1 seconds ago 
    def test_since_when_with_record_created_one_hour_and_one_second_ago(self) :
        seconds_ago = 60*60 + 1 
        notification = self.create_notification(seconds_ago=seconds_ago)
        self.assertEqual(notification.since_when(), '1 hour ago')

    # test since_when with a record created one hour and 59 minutes before 
    def test_since_when_with_a_record_created_2_hours_minus_one_second(self) :
        seconds_ago = 60*60 + 59*60 +59 
        notification = self.create_notification(seconds_ago=seconds_ago)
        self.assertEqual(notification.since_when(), '1 hour ago')
    
    # test since_when with a record created 2 hours ago 
    def test_since_when_with_a_record_created_2_hours_ago(self) :
        seconds_ago = 7200 
        notification = self.create_notification(seconds_ago=seconds_ago)
        self.assertEqual(notification.since_when(), '2 hours ago')
    
    # test since_when with a record created 23 hours, 59 minutes and 59 seconds ago
    def test_since_when_with_a_record_created_before_one_day_minus_one_second(self) :
        seconds_ago = 23*60*60 + 59*60 + 59
        notification = self.create_notification(seconds_ago=seconds_ago)
        self.assertEqual(notification.since_when(), '23 hours ago')
    
    # test since_when with a record created exactly 24 hours ago
    def test_since_when_with_a_record_created_24hours_ago(self) :
        seconds_ago = 24*3600
        notification = self.create_notification(seconds_ago=seconds_ago)
        self.assertEqual(notification.since_when(), 'Yesterday')

    # test since_when with a record created 24 hours and 1 second ago
    def test_since_when_with_record_created_24hours_and_one_second_ago(self) :
        seconds_ago = 24*3600 + 1
        notification = self.create_notification(seconds_ago=seconds_ago)
        self.assertEqual(notification.since_when(), 'Yesterday')
    
    # test since_when with a record created 2 days minus one second ago 
    def test_since_when_with_record_created_2days_minus_one_second_ago(self) :
        seconds_ago = 48*3600 - 1 
        notification = self.create_notification(seconds_ago=seconds_ago)
        self.assertEqual(notification.since_when(), 'Yesterday')
    
    # test since_when with a record created 48 hours exactly ago 
    def test_since_when_with_record_created_48hours_ago(self) :
        notification = self.create_notification(seconds_ago=48*3600)
        self.assertEqual(notification.since_when().date(), datetime(2023, 6, 28).date())


# class to test the operation of get_list_of_my_friemds 
class GetListOfMyFriendsViewTests(TestCase) :
    # function that creates a user and associated FriendsList 
    def get_user_and_friendslist(self) :
        user = User.objects.create_user(username='amine', password='1234')
        friend1 = User.objects.create_user(username='friend1', password='friend1')
        friend2 = User.objects.create_user(username='friend2', password='friend2')
        Friends_list = FriendsList.objects.create(belongs_to=user)
        Friends_list.friends.set([friend1, friend2])
        return user, Friends_list
    
    # test the get_list_of_my_friends with unauthenticated user 
    def test_get_list_of_my_friends_with_unauthenticated_user(self) :
        target_url = reverse('friends:my_friends')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
    
    # test get_list_of_my_friends with authenticated user with get request
    def test_get_list_of_my_friends_with_get_request(self) :
        # get the user and it's friends list
        user, friends_list = self.get_user_and_friendslist()
        target_url = reverse('friends:my_friends')
        # authenticate the user 
        self.client.login(username='amine', password='1234')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context['friends'], friends_list.friends.all())
        self.assertEqual(response.context['friends_list'], friends_list)
        self.assertTrue(FriendsList.objects.exists())
        self.assertEqual(len(friends_list.friends.all()), 2)
        self.assertContains(response, 'friend1')
        self.assertContains(response, 'friend2')

    # test get_list_of_my_friends with post request 
    def test_get_list_of_my_friends_with_post_request_and_no_conversation(self) :
        # create a user with two friends 
        user, friends_list = self.get_user_and_friendslist()
        target_url = reverse('friends:my_friends')
        # authenticate the user and send a get request
        self.client.login(username='amine', password='1234')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'friend1')
        self.assertContains(response, 'friend2')
        # Click 'Message' button which sends a post request to same url
        response = self.client.post(target_url, {'username' : 'friend1'})
        # check that a Conversation object has been created 
        self.assertTrue(Conversation.objects.exists())
        self.assertTrue(Conversation.objects.filter(member_one=user, member_two=User.objects.get(username='friend1')).exists())
        # check the session 
        created_conversation = Conversation.objects.get(member_one=user, member_two=User.objects.get(username='friend1'))
        session_data = self.client.session
        self.assertEqual(session_data.get('conversations'), [created_conversation.to_json()])
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context['friends'], friends_list.friends.all())
        self.assertQuerysetEqual(response.context['conversations'], Conversation.objects.filter(member_one=user, member_two=User.objects.get(username='friend1')))
        # click 'Message' for friend2 
        response = self.client.post(target_url, {'username' : 'friend2'})
        # check that Conversation object has been created 
        self.assertTrue(Conversation.objects.filter(member_one=user, member_two=User.objects.get(username='friend2')).exists())
        self.assertTrue(len(Conversation.objects.all()), 2)
        # check session 
        session_data = self.client.session
        self.assertEqual(session_data.get('conversations'), [conv.to_json() for conv in Conversation.objects.filter(member_one=user)])
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context['friends'], friends_list.friends.all())
        self.assertEqual(len(response.context['conversations']), 2)
        self.assertQuerysetEqual(response.context['conversations'], Conversation.objects.filter(member_one=user))
        self.assertContains(response, 'No messages yet')
        # send a get request and check session 
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get('conversations') is not None)

# class to test the operation of close_conversation View 
class CloseConversationViewTests(TestCase) :
    def create_user_and_friends(self) :
        user = User.objects.create_user(username='amine', password='1234')
        user_friends_list = FriendsList.objects.create(belongs_to=user)
        friend_one = User.objects.create_user(username='friend_one', password='friend_one')
        friend_two = User.objects.create_user(username='friend_two', password='friend_two')
        user_friends_list.friends.set([friend_one, friend_two])
        return user, user_friends_list
    # test with unauthenticated user 
    def test_close_conversation_with_unauthenticated_user(self) :
        target_url = reverse('friends:close_conversation')
        response = self.client.post(target_url,{})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")

    # test with a user who does not exist 
    def test_close_conversation_with_unexisting_user(self) :
        # create a user and authenticate him
        User.objects.create_user(username='amine', password='1234')
        self.client.login(username='amine', password='1234')
        target_url = reverse('friends:close_conversation')
        # send a post request with username that corresponds to no user
        response = self.client.post(target_url, {'username' : 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('friends:my_friends'))
        # check messages 
        my_messages = list(messages.get_messages(request=response.wsgi_request))
        self.assertEqual(len(my_messages), 1) 
        for message in my_messages :
            self.assertEqual(message.tags, 'error')
            self.assertEqual(message.message, 'Oops ! something went wrong')
    
    # test with authenticated user closing a conversation he opened
    def test_close_conversation_with_authenticated_user_closing_a_conversation_he_opened(self) :
        # create a user and authenticate him 
        user, friends_list = self.create_user_and_friends()
        self.client.login(username='amine', password='1234')
        # check my_friends using get request 
        target_url = reverse('friends:my_friends')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context['friends'], FriendsList.objects.get(belongs_to=user).friends.all())
        self.assertContains(response, 'friend_one')
        self.assertContains(response, 'friend_two')
        # send post request to message 'friend_one'
        response = self.client.post(target_url, {'username' : 'friend_one'})
        self.assertEqual(response.status_code, 200)
        # check that a conversation object has been created 
        self.assertTrue(Conversation.objects.exists())
        self.assertQuerysetEqual(response.context['conversations'], Conversation.objects.filter(member_one=user, member_two=User.objects.get(username='friend_one')))
        # check session data 
        self.assertEqual(self.client.session.get('conversations'), [conv.to_json() for conv in Conversation.objects.all()])
        self.assertEqual(len(self.client.session.get('conversations')), 1)
        # send a get request 
        response = self.client.get(target_url)
        # check for 'conversations' in context data
        self.assertQuerysetEqual(response.context['conversations'], [Conversation.objects.get(member_one=user, member_two=User.objects.get(username='friend_one'))])
        self.assertCountEqual(response.context['friends'], friends_list.friends.all())
        self.assertContains(response, 'No messages yet')
        self.assertEqual(self.client.session.get('conversations'), [conv.to_json() for conv in Conversation.objects.filter(member_one=user, member_two=User.objects.get(username='friend_one'))])
        # close the discussion by sending a post request 
        target_url = reverse('friends:close_conversation')
        response = self.client.post(target_url, {'username' : 'friend_one'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('friends:my_friends'))
        # check session data 
        self.assertEqual(self.client.session.get('conversations'), [])
        # perform a get request and check context data and session
        response = self.client.get(reverse('friends:my_friends'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['conversations'], [])

# class to test the operation of send_message View
class SendMessageViewTests(TestCase) :
    # create a user with a friends_list 
    def create_user_and_friends_list(self) :
        user = User.objects.create_user(username='amine', password='1234')
        # create two friend users
        friend1 = User.objects.create_user(username='friend1', password='friend1')
        friend2 = User.objects.create_user(username='friend2', password='friend2')
        friends_list = FriendsList.objects.create(belongs_to = user)
        friends_list.friends.set([friend1, friend2])
        return user, friend1, friend2
    # test with unauthenticated user 
    def test_send_message_with_unauthenticated_user(self) :
        # we pass as an argument a username that doesn't exist
        # it doesn't matter since authentication will prevent the handling logic
        target_url = reverse('friends:send_message', args=('test',))
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
    
    # test send_message with a username who does not exist 
    def test_send_message_to_unexisting_user(self) :
        # create a user and authenticate him
        User.objects.create_user(username='amine', password='1234')
        self.client.login(username='amine', password='1234')
        target_url = reverse('friends:send_message', args=('not_existing',))
        response = self.client.post(target_url, {'message' : 'test message'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('friends:my_friends'))
        # check for messages 
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'error')
            self.assertEqual(message.message, 'Oops, something went wrong !')
    
    # test send_message to a friend with whom a Conversation object doesn't exist
    def test_send_message_to_a_friend_with_whom_no_conversation_object_exists(self) :
        # create a user with his friends_list and authenticate him
        self.create_user_and_friends_list()
        # authenticate the user 
        self.client.login(username='amine', password='1234')
        # try send a message to one of his friends
        target_url = reverse('friends:send_message', args=('friend1',))
        response = self.client.post(target_url, {'message' : 'test message'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('friends:my_friends'))
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'error')
            self.assertEqual(message.message, 'something went wrong !')

    # test send_message to a user not in friends_list 
    def test_send_message_to_user_not_in_friends_list(self) :
        # create a user with friends_list containing friend1 and friend2
        self.create_user_and_friends_list()
        # create a user who's not in friends list 
        not_friend = User.objects.create_user(username='notfriend', password='notfriend')
        # authenticate the user 
        self.client.login(username='amine', password='1234')
        target_url = reverse('friends:send_message', args=('notfriend',))
        response = self.client.post(target_url, {'message' : 'test message'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('friends:my_friends'))
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'error')
            self.assertEqual(message.message, 'unauthorized action, you are not friends!')       

    # test send_message with empty text
    def test_send_message_with_empty_text(self) :
        # create a user and freinds_list containing two friends
        user, friend1, friend2 = self.create_user_and_friends_list()
        # create a Conversation instance with two mwmbers
        Conversation.objects.create(member_one=friend1, member_two=user)
        # authenticate user and send empty message to friend1
        self.client.login(username='amine', password='1234')
        target_url = reverse('friends:send_message', args=('friend1',))
        response = self.client.post(target_url, {'message' : '    '})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('friends:my_friends'))
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'error')
            self.assertEqual(message.message, 'invalid message, Enter some text')
    
    # test send_message view with get request
    def test_send_message_with_get_request(self) :
        # create a user and friends_list containing two friends 
        self.create_user_and_friends_list()
        # create the user receiver of message 
        receiver = User.objects.create_user(username='receiver', password='receiver')
        # authenticate user
        self.client.login(username='amine', password='1234')
        target_url = reverse('friends:send_message', args=('friend1',))
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'error')
            self.assertEqual(message.message, 'undefined URL !')
        
        