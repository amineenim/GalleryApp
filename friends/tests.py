from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from .models import FriendshipRequest
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




