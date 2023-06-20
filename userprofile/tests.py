from datetime import date
from django.test import TestCase
from django.urls import reverse
from .models import UserProfile
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
# Create your tests here.

# class to test the operation of get_my_profile View 
class GetMyProfileViewTests(TestCase) :
    def create_user_profile(self, first_name, last_name, yaer, month, day, bio, country) :
        self.user = User.objects.create_user(username='userr', password='userr')
        image_file = SimpleUploadedFile('image.png', b"content_file", 'image/png')
        birthdate = date(year=yaer, month=month, day=day)
        return UserProfile.objects.create(first_name=first_name,
                                   last_name=last_name,
                                   birthdate=birthdate,
                                   bio = bio,
                                   profile_picture=image_file,
                                   country = country,
                                   user=self.user)
    
    # tests with an unauthenticated user 
    def test_get_my_profile_with_unauthenticated_user(self) :
        target_url = reverse('profile:my_profile')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
    
    # tests the get_my_profile view with a get request when userProfile data doesn't exist
    def test_get_my_profile_with_get_request_and_user_profile_data_not_existing(self) :
        # create a user and authenticate him 
        User.objects.create_user(username='test', password='123')
        self.client.login(username='test', password='123')
        target_url = reverse('profile:my_profile')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['is_first_time'], True)
        self.assertContains(response, 'Add data')

    # tests the get-my_profile view with a get request when userprofile for the user exists
    def test_get_my_profile_with_get_request_while_having_a_corresponding_user_profile_data(self) :
        # create a corresponding userProfile for the user 
        profile_data = self.create_user_profile('amine', 'maourid', 1995, 5, 23, "i love travel", 'Morocco')
        # authenticate the user of the profile 
        self.client.login(username='userr', password='userr')
        target_url = reverse('profile:my_profile')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['is_first_time'], False)
        self.assertEqual(response.context['user_profile_data'], profile_data)
        self.assertContains(response, 'amine')

    # tests the get_my_profile view with a post request when the user is creating the data for the first time
    def test_get_my_profile_with_post_request_with_user_adding_his_data_for_the_first_time(self) :
        # create a user and authenticate him
        User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
        target_url = reverse('profile:my_profile')
        response = self.client.post(target_url,{
            'first_name' : 'amine',
            'last_name' : 'maourid',
            'birthdate' : date(1995, 5, 23),
            'bio' : 'hello world!',
            'profile_picture' : SimpleUploadedFile('test.jpg', b"content_file", 'image/jpeg'),
            'country' : 'Morocco',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile:my_profile'))


