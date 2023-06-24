from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
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

    # test send_friendship_request to a user which does not exist 
    def test_send_friendship_request_to_unexisting_user(self) :
        # create a user and autneticate him 
        User.objects.create_user(username='amine', password='test')
        self.client.login(username='amine', password='test')
        # i pass as a username argument 'not_existing' which doesn't refer to any user
        target_url = reverse('friends:send_request', args=('not_existing',))
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        
