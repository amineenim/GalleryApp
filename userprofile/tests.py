from django.test import TestCase
from django.urls import reverse
from . import urls
# Create your tests here.

# class to test the operation of get_my_profile View 
class GetMyProfileViewTests(TestCase) :
    # tests with an unauthenticated user 
    def test_get_my_profile_with_unauthenticated_user(self) :
        target_url = reverse('profile:my_profile')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")