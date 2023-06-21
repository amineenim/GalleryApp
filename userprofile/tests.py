from datetime import date
from django.test import TestCase
from django.urls import reverse
from .models import UserProfile
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib import messages
from .forms import UserProfileCreateForm
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
        user = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
        target_url = reverse('profile:my_profile')
        get_response = self.client.get(target_url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.context['is_first_time'], True)
        self.assertContains(get_response, 'Add data')
        # create an image file
        image_file = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")


        data = {
            'first_name' : 'amine',
            'last_name' : 'maourid',
            'birthdate' : date(1995, 5, 23),
            'bio' : 'hello world!',
            'profile_picture' : image_file,
            'country' : 'US',
        }
        files = {'profile_picture': image_file}

        response1 = self.client.post(target_url, data)
        self.assertEqual(response1.status_code, 302)
        self.assertRedirects(response1, target_url)

        # check for messages associated with the request 
        my_messages = list(messages.get_messages(response1.wsgi_request))
        # check that we only have one message 
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'success') # check it's a success message
            self.assertEqual(message.message, 'Profile data added with success') # check the text of the message
        
        form = UserProfileCreateForm(data, files)
        if not form.is_valid() :
            print(form.errors)
        self.assertTrue(form.is_valid())
        # check that a UserProfile instance was created 
        self.assertTrue(UserProfile.objects.exists())
        # go to the redirecy url and check that it contains the data just created 
        response2 = self.client.get(target_url)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.context['is_first_time'], False)
        self.assertEqual(response2.context['user_profile_data'], UserProfile.objects.filter(user=user).first())
        self.assertContains(response2, 'Save changes')
        self.assertContains(response2, 'maourid')
        

    # tests the get_my_profile view with a post request when the user has already profile data 
    def test_get_my_profile_with_post_request_with_user_having_already_profile_data(self) :
        # create a user profile 
        user_profile_data = self.create_user_profile(
            'amine',
            'maourid',
            1998,
            6,
            14,
            'hello world',
            'AU'
        )
        # authenticate the user owner of the UserProfile data 
        self.client.login(username='userr', password='userr')
        target_url = reverse('profile:my_profile')
        # send a get request and check that data already exists
        get_response = self.client.get(target_url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.context['is_first_time'], False)
        self.assertEqual(get_response.context['user_profile_data'], user_profile_data)
        self.assertContains(get_response, 'amine')
        # test for the post request, which will update the data 
        image_file = SimpleUploadedFile('image.png', b"content_file", 'image/png')
        data = {
            'first_name' : 'enima',
            'last_name' : 'maourid',
            'birthdate' : date(1995, 5, 23),
            'bio' : 'hello world',
            'profile_picture' : image_file,
            'country' : 'AU',
        } 
        post_response = self.client.post(target_url,data)
        files = {'profile_picture' : image_file}
        form = UserProfileCreateForm(data=data, files=files)
        self.assertTrue(form.is_valid())
        # check the redirect 
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, target_url)
        # check for the messages generated by the messages framework, tranform into a list
        my_messages = list(messages.get_messages(post_response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'success')
            self.assertEqual(message.message, 'profile data modified succesefully')
        
        # check for the redirect_url if it contains the new data 
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['is_first_time'], False)
        self.assertContains(response, 'enima')
        self.assertContains(response, date(1995, 5, 23))
        self.assertContains(response, 'Save changes')
    
    # tests the get_my_profile view with invalid birthdates 
    def test_get_my_profile_with_post_request_and_invalid_birthdate_beyond_the_actual_date(self) :
        # create a user and authenticate him
        User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        # prepare data to pass to the form 
        image_file = SimpleUploadedFile('test.jpg', b"file_content", 'image/jpeg')
        data = {
            'first_name' : 'amine',
            'last_name' : 'maourid',
            'birthdate' : date(2023, 6, 24),
            'bio' : 'hello world',
            'profile_picture' : image_file,
            'country' : 'US'
        }
        target_url = reverse('profile:my_profile')
        files = {'profile_picture' : image_file }
        form = UserProfileCreateForm(data=data, files=files)
        # the form only checks for a valid date , after more advanced analyses of dates are performed
        self.assertTrue(form.is_valid())
        response = self.client.post(target_url, data)
        # check that the response status is 200 and that an error_birthdate context variable is passed to the view
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error_birthdate'], 'unvalid birthdate')
        # check that no UserProfile instance was created 
        self.assertFalse(UserProfile.objects.exists())
        # go the my profile url and check it's empty 
        response1 = self.client.get(target_url)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.context['is_first_time'], True)
        self.assertContains(response1, 'Add data')
    
    # tests the get_my_profile view in post request with a date in the last 5 years  
    def test_get_my_profile_with_post_request_and_invalid_birthdate_in_last_five_years(self) :
        # create a user and authenticate him 
        User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
        # data to pass to the form 
        image_file = SimpleUploadedFile('test.png', b"file_content", 'image/png')
        # test done in 21/06/2023 
        data1 = {
            'first_name' : 'test',
            'last_name' : 'test',
            'birthdate' : date(2018, 7, 1),
            'bio' : 'hello world',
            'profile_picture' : image_file,
            'country' : 'AU'
        }

        files = {'profile_picture' : image_file }

        form1 = UserProfileCreateForm(data=data1, files=files)
        # check the form is valid 
        self.assertTrue(form1.is_valid())

        target_url = reverse('profile:my_profile')
        response = self.client.post(target_url, data1)
        
        # check that both responses return a 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['error_birthdate'])
        self.assertContains(response, 'unvalid date pick a date between')
        # check that no UserProfile instance is created 
        self.assertFalse(UserProfile.objects.exists())
        # request my profile url with get request and check it's empty 
        get_response = self.client.get(target_url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.context['is_first_time'], True)
        self.assertContains(get_response, 'Add data')
    
    # tests the get_my_profile view in post request with a date before 70 years 
    def test_get_my_profile_with_post_request_and_invalid_birthdate_before_seventy_years(self) :
        # create a user and authenticate him 
        User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
        # data to pass to the form 
        image_file = SimpleUploadedFile('test.png', b"file_content", 'image/png')
       
        data2 = {
            'first_name' : 'test',
            'last_name' : 'test',
            'birthdate' : date(1953, 5, 20),
            'bio' : 'hello world',
            'profile_picture' : image_file,
            'country' : 'AU'
        }
        files = {'profile_picture' : image_file }

        form2 = UserProfileCreateForm(data=data2, files=files)
        # check the form is valid 
        self.assertTrue(form2.is_valid()) 

        target_url = reverse('profile:my_profile')
        response = self.client.post(target_url, data2)
        
        
        # check that both responses return a 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['error_birthdate'])
        self.assertContains(response, 'unvalid date pick a date between')
        # check that no UserProfile instance is created 
        self.assertFalse(UserProfile.objects.exists())
        # request my profile url with get request and check it's empty 
        get_response = self.client.get(target_url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.context['is_first_time'], True)
        self.assertContains(get_response, 'Add data')

        


