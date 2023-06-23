from datetime import date
from django.test import TestCase
from django.urls import reverse
from .models import UserProfile
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib import messages
from .forms import UserProfileCreateForm
from django_countries.fields import Country
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

        
# class to test the search functionnality in get_my_profile view 
class SearchInGetMyProfileViewTests(TestCase) :
    # function that creates and returns a user
    def create_user(self, username, password) :
        return User.objects.create_user(username=username, password=password)
    
    # tests the search functionnality with an empty string 
    def test_search_with_empty_string(self) :
        # create a user and authenticate him 
        self.create_user('test', '1234')
        self.client.login(username='test', password='1234')
        empty_string = ''
        target_url = f"{reverse('profile:my_profile')}?search={empty_string}"
        response = self.client.get(target_url)
        # check the response status
        self.assertEqual(response.status_code, 200)
        # check that the 'search_results' and 'searched_value' variables are not passed as context variables
        self.assertNotIn('search_results', response.context)
        self.assertNotIn('searched_value', response.context)
    
    # tests the search functionnality with a user looking for another user that exists 
    def test_search_with_user_looking_for_another_user_who_exists(self) :
        # create the user to search for 
        self.create_user(username='search_me', password='1234')
        # create a user and authenticate him
        User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
        # since the search looks for records whose username contains the input in search this corresponds to "search_me" user
        search_string = 'ch_me'
        target_url = f"{reverse('profile:my_profile')}?search={search_string}"
        response = self.client.get(target_url)
        # check for response status and context variables 
        self.assertEqual(response.status_code, 200)
        self.assertIn('search_results', response.context)
        self.assertIn('searched_value', response.context)
        self.assertQuerysetEqual(response.context['search_results'], [User.objects.filter(username='search_me').first()])
        # check that the value typed in search will prefill the search input
        self.assertContains(response, 'ch_me')
        # check that the div under the search inout will display "search_me" as a result 
        self.assertContains(response, 'search_me')
    
    # tests the search functionnality with a user looking for a user not existing 
    def test_search_with_user_looking_for_a_user_not_existing(self) :
        # create a user and authenticate him 
        self.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
        search_string = 'not_existing'
        target_url = f"{reverse('profile:my_profile')}?search={search_string}"
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        # check for the response context 
        self.assertIn('search_results', response.context)
        self.assertIn('searched_value', response.context)
        self.assertQuerysetEqual(response.context['search_results'], [])
        self.assertEqual(response.context['searched_value'], search_string)
        self.assertContains(response, 'No results for your search')
    
    # tests the search functionnality with a search that matches more than a user 
    def test_search_with_search_input_matching_more_than_a_single_user(self) :
        user1 = self.create_user(username='userone', password='1234')
        user2 = self.create_user(username='usertwo', password='45678')
        # create a user and authenticate him
        User.objects.create_user(username='amine', password='test')
        self.client.login(username='amine', password='test')
        # this search string exists in both the users 1 and 2 username
        search_string = 'user'
        target_url = f"{reverse('profile:my_profile')}?search={search_string}"
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        # check for response's context
        self.assertIn('search_results', response.context)
        self.assertIn('searched_value', response.context)
        self.assertContains(response, 'userone')
        self.assertContains(response, 'usertwo')
        self.assertEqual(response.context['searched_value'], search_string)
        # check that the iterables are equal without regard to the order
        self.assertCountEqual(response.context['search_results'], [user1, user2])

# class to test get_profile view which allows a user to see am=nother user profile 
class GetProfileViewTests(TestCase) :
    # test get_profile view with unauthenticated user 
    def test_get_profile_with_unauthenticated_user(self) :
        target_url = reverse('profile:view_profile', args=('test',))
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
    
    # test get_profile with user requesting a user with username not existing
    def test_get_profile_with_user_not_existing(self) :
        # create a user and authenticate him
        User.objects.create_user(username='amine', password='1234')
        self.client.login(username='amine', password='1234')
        # we don't have a user with username 'alpha' for example
        username = 'alpha'
        target_url = reverse('profile:view_profile', args=(username,))
        response = self.client.get(target_url)
        # check for reponse status and messages 
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        # get messages and tranform in list 
        my_messages = list(messages.get_messages(response.wsgi_request))
        for message in my_messages :
            self.assertEqual(message.tags, 'error')
            self.assertEqual(message.message, 'Not found 404')
    
    # test the get_profile view with an existing user but UserProfile instance associated with him not existing
    def test_get_profile_with_existing_user_and_no_user_profile_data_associated(self) :
        # create a user , this user is the one we're going to request his profile
        User.objects.create_user(username='i_exist', password='test')
        # create a user and authenticate him
        User.objects.create_user(username='amine', password='1234')
        self.client.login(username='amine', password='1234')
        target_url = reverse('profile:view_profile', args=('i_exist',))
        response = self.client.get(target_url)
        # check for response 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['username'], 'i_exist')
        self.assertNotIn('user_profile_data', response.context)
        self.assertContains(response, 'No Profile data availabe for i_exist')
    
    # test get_profile view with existing user and UserProfile data for the user existing
    def test_get_profile_with_user_having_profile_data(self) :
        # create a user and a UserProfile instance associated to him
        user_with_profile_data = User.objects.create_user(username='test', password='test')
        image_file = SimpleUploadedFile('profile.jpg', b"file_content", 'image/jpeg')
        profile_data = UserProfile.objects.create(
            first_name = 'amine',
            last_name = 'enima',
            birthdate = date(1999, 9, 9),
            bio = 'hello world',
            user = user_with_profile_data,
            profile_picture = image_file,
            country = 'US'
        )
        # create a user and authenticate him
        User.objects.create_user(username='foo', password='1234')
        self.client.login(username='foo', password='1234')
        # set the url to request with the username 'test' since we gonna request his profile
        target_url = reverse('profile:view_profile', args=('test',))
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        # check for context variables passed to the view 
        self.assertIn('user_profile_data', response.context)
        self.assertIn('username', response.context)
        self.assertIn('country_data', response.context)
        self.assertEqual(response.context['username'], 'test')
        country_data = Country('US')
        self.assertEqual(response.context['country_data'], country_data)
        self.assertEqual(response.context['user_profile_data'], profile_data)
        # check for the content of the rendered view 
        self.assertContains(response, 'amine')
        self.assertContains(response, 'enima')
        self.assertContains(response, 'hello world')
        self.assertContains(response, country_data.name)