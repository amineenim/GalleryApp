from datetime import timedelta
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from .models import PasswordResetToken, EmailVerificationToken, Photo, Category
from django.urls import reverse
from django.core import mail
from django.contrib import messages
from django.utils import timezone
from .forms import CreateUserForm, PhotoForm
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from unittest.mock import patch 
from django.template.loader import render_to_string
from django.core.files.uploadedfile import SimpleUploadedFile
import os 

# Create your tests here.
# class to test the operation of reset_password view
class PasswordResetViewTests(TestCase) :
    # test with authenticated user 
    def test_reset_password_with_authenticated_user(self) :
        # create a user and authenticate him
        User.objects.create_user(username='amine', password='1234')
        self.client.login(username='amine', password='1234')
        target_url = reverse('reset_password')
        # test for get request
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        # test for post request
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
    
    # test with unauthenticated user in get request 
    def test_reset_password_with_unauthenticated_user_and_get_request(self) :
        target_url = reverse('reset_password')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'an email with a link to reset your password will be sent to your email address')
    
    # the following tests serve for the form where the user enters his email
    # address in order to get a reset password link 

    # test with unauthenticated user and post request with empty email value submitted
    def test_reset_password_with_post_request_and_empty_value_for_email_input(self) :
        target_url = reverse('reset_password')
        response = self.client.post(target_url, {'email' : ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter an email address, empty value submitted')
        self.assertContains(response, 'an email with a link to reset your password will be sent to your email address')

    # test with unauthenticated user and post request , with a value for emaail invalid 
    def test_reset_password_with_post_request_and_invalid_email_address(self) :
        target_url = reverse('reset_password')
        # pass an invalid email 
        response = self.client.post(target_url, {'email' : 'aminemaourid'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'invalid email address')
        self.assertContains(response, 'an email with a link to reset your password will be sent to your email address')
    
    # test with unauthenticated user and a valid email which doesn't correspond to no user
    def test_reset_password_with_post_request_and_valid_email_referencing_no_user(self) :
        target_url = reverse('reset_password')
        # valid email, not belonging to no user 
        response = self.client.post(target_url, {'email' : 'test.test@gmail.com'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Given email address does not correspond to a user')
        self.assertContains(response, 'an email with a link to reset your password will be sent to your email address')

    # test with unauthenticated user and a valid email belonging to a user 
    # override the email backend to temporarily use 'locmem' which allows
    # storing the sent mails in memory instead of sending them via SMTP
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_reset_password_with_post_request_and_valid_email_belonging_to_a_user(self) :
        # create a user 
        user = User.objects.create_user(username='amine', email='amine_maourid@gmail.com', password='1234')
        target_url = reverse('reset_password')
        response = self.client.post(target_url, {'email' : 'amine_maourid@gmail.com'})
        # check for response status
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password reset url sent, check your email')
        # check that a PasswordResetToken object has been created 
        self.assertTrue(PasswordResetToken.objects.exists())
        self.assertTrue(PasswordResetToken.objects.filter(user=user).exists())
        # check for mail sending 
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        # check email attributes 
        self.assertEqual(sent_mail.subject, 'Password Reset')
        self.assertEqual(sent_mail.from_email, 'aminemaourid1@gmail.com')
        self.assertEqual(sent_mail.to, ['amine_maourid@gmail.com'])
        # check for mail content 
        self.assertIn('to reset your password, click the following url :', sent_mail.body)
        reset_url = f"http://localhost:8000/gallery/accounts/resetpassword/?token={PasswordResetToken.objects.first().token}"
        self.assertIn(reset_url, sent_mail.body)
    
    # the following tests concern the password reset form where the user 
    # enters the new password and confirmation 

    # function that simulates the scenario where a user enters his email address and gets
    # a password reset token
    def simulate_getting_password_reset_token(self) :
        user = User.objects.create_user(username='amine', password='1234', email='amine_maourid@gmail.com')
        # submit the email corresponding to the user 'amine'
        self.client.post(reverse('reset_password'), {'email' : 'amine_maourid@gmail.com'})
        # get the token generated 
        generated_token = PasswordResetToken.objects.filter(user=user).first()
        token = generated_token.token 
        return token 
    
    # test reset_password using get request and appending a valid token
    def test_reset_password_with_get_request_after_getting_a_token(self) :
        token = self.simulate_getting_password_reset_token()
        target_url = f"{reverse('reset_password')}?token={token}"
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'password must be at least 8 characters')
        self.assertContains(response, 'Enter your password')
        self.assertContains(response, 'Confirm password')
        self.assertEqual(response.context['token'], PasswordResetToken.objects.get(token=token))
    
    # test reset_password using get request and invalid token 
    def test_reset_password_with_get_request_and_invalid_token(self) :
        token = self.simulate_getting_password_reset_token()
        # check that a PasswordResetToken object has been created
        self.assertTrue(PasswordResetToken.objects.exists())
        # alter the token so it becomes invalid 
        
        target_url = f"{reverse('reset_password')}?token={token}7"
        # send a get request 
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('reset_password'))
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'error')
            self.assertEqual(message.message, 'invalid Token')
    
    # test reset_password using get request and expired token 
    def test_reset_password_with_get_request_and_expired_token(self) :
        # create a user instance to which the token will be associated 
        user = User.objects.create_user(username='amine', password='1234')
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        # set the created_at to 1hour and 1 second before so the expires_at
        # would be 1 second ago 
        time_now = timezone.now()
        created_at = time_now - timedelta(hours=1, seconds=1)
        token_object = PasswordResetToken.objects.create(
            user = user,
            token = token,
            created_at = created_at,
            expires_at = time_now - timedelta(seconds=1)
        )
        target_url = f"{reverse('reset_password')}?token={token}"
        # send a get request
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('reset_password'))
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'error')
            self.assertEqual(message.message, 'Token expired, Get a new one to reset your Password')
        
    # test reset_password using get request and token expiring after a few seconds
    def test_reset_password_with_get_request_and_token_near_expiring(self) :
        user = User.objects.create_user(username='amine', password='1234')
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        # create a token object whith token having 1s left before expiring
        time_now = timezone.now()
        token_object = PasswordResetToken.objects.create(
            user=user,
            token = token,
            created_at = time_now - timedelta(minutes=59, seconds=59),
            expires_at = time_now + timedelta(seconds=1)
        )
        target_url = f"{reverse('reset_password')}?token={token}"
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['token'], token_object)
        self.assertContains(response, 'Reset Paasword')
        self.assertContains(response, 'Enter your password')
        self.assertContains(response, 'Confirm password')
        self.assertEqual(response.context['token'], PasswordResetToken.objects.filter(user=user).first())
    
    # test reset password with post request and password1 field missing
    def test_reset_password_with_post_request_and_password1_missing(self) :
        # simulate a user that gets a token to reset his forgotten password
        token = self.simulate_getting_password_reset_token()
        # build the url which will be sent by enail to the user 
        password_reset_url = f"{reverse('reset_password')}?token={token}"
        # send a get request to this url, since after clicking on it the user will hit the url with a get request
        response = self.client.get(password_reset_url)
        # check that we land on the page with the form for password and confirmation since token is valid
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter your password')
        self.assertContains(response, 'Confirm password')
        # check that context data contains the PasswordResetToken object
        self.assertEqual(response.context['token'], PasswordResetToken.objects.get(token=token))
        # simulate sending a post request while password1 field is empty
        target_url = reverse('reset_password')
        # get user and token value from response context object
        user = response.context['token'].user
        data = {'password1' : '',
                'password2' : 'blabla123',
                'token' : token,
                'user' : user}
        response = self.client.post(target_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], 'both fields are required')
        self.assertEqual(response.context['token'], PasswordResetToken.objects.get(user=user))
        # check that the error message is displayed
        self.assertContains(response, 'both fields are required')
        self.assertContains(response, 'Enter your password')

        # same thing if password2 which corresponds to password confirmation is missing
        data = {'password1' : 'test123',
                'password2' : '',
                'token' : token,
                'user' : user}
        response = self.client.post(target_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], 'both fields are required')
        self.assertEqual(response.context['token'], PasswordResetToken.objects.get(token=token))
        self.assertContains(response, 'both fields are required')
        self.assertContains(response, 'Enter your password')
        self.assertContains(response, 'Confirm password')

        # if the two fields are submitted but with invalid password 
        # the password is the same as username so password_validator will reject it
        data = {'password1' : 'amine',
                'password2' : 'amine',
                'token' : token,
                'user' : user}
        response = self.client.post(target_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['token'], PasswordResetToken.objects.get(token=token))
        self.assertTrue(len(response.context['errors']) > 1)
        self.assertContains(response, 'Enter your password')
        self.assertContains(response, 'Confirm password')
        self.assertQuerysetEqual(response.context['errors'], 
                                 ['The password is too similar to the username.', 
                                  'This password is too short. It must contain at least 8 characters.'])
        # check errors are displayed
        self.assertContains(response, 'The password is too similar to the username.')
        self.assertContains(response, "This password is too short. It must contain at least 8 characters.")


        # the two fields are submitted, the password is valid but it password confirmation mismatches password
        data = {'password1' : 'test123@',
                'password2' : 'test123',
                'token' : token,
                'user' : user}
        response = self.client.post(target_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['token'], PasswordResetToken.objects.get(token=token))
        self.assertEqual(response.context['error'], "The two passwords are not matching")
        self.assertContains(response, 'Enter your password')
        self.assertContains(response, 'Confirm password')
        self.assertContains(response, "The two passwords are not matching")

        # all is set correctly
        data = {'password1' : 'test123@',
                'password2' : 'test123@',
                'token' : token,
                'user' : user}
        response = self.client.post(target_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        # check that user is authenticated after successefully reseting the password
        self.assertTrue(User.objects.get(username='amine').is_authenticated)
        # check messages 
        my_messages = list(messages.get_messages(request=response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'success')
            self.assertEqual(message.message, 'Password reset successefully !')
        # check that the PasswordResetToken has been removed
        self.assertFalse(PasswordResetToken.objects.filter(token=token).exists())
        # check that the user password is now updated and set to the new value
        # using this method instead of directly grabbing user.password because the
        # stored value is hached 
        self.assertTrue(User.objects.get(username='amine').check_password('test123@'))

# class to test the operation of loginUser view
class LoginUserViewTests(TestCase) :
    # test with authenticated user 
    def test_login_user_with_authenticated_user(self) :
        User.objects.create_user(username='amine', password='1234')
        self.client.login(username='amine', password='1234')
        target_url = reverse('login')
        # check for get request
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        # check for post request 
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
    
    # test with unauthenticated user and get request 
    def test_login_user_with_unauthenticated_user_and_get_request(self) :
        target_url = reverse('login')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Authenticate here and enjoy our plateform')
        self.assertContains(response, 'Enter your username')
        self.assertContains(response, 'Enter your password')

    # test with unauthenticated user using a post request and username or password are 
    # missing after form submission
    def test_login_user_using_post_request_with_empty_value_in_one_field(self) :
        target_url = reverse('login')
        response = self.client.post(target_url, {
            'username' : '', 
            'password' : 'test1234'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error_message'], 'both fields are required')
        # check for error display
        self.assertContains(response, 'both fields are required')
        self.assertContains(response, 'Enter your username')
        self.assertContains(response, 'Enter your password')

        # submit form with password field empty
        response = self.client.post(target_url, {
            'username' : 'amine',
            'password' : ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error_message'], 'both fields are required')
        # check for error display 
        self.assertContains(response, 'both fields are required')
        self.assertContains(response, 'Enter your username')
        self.assertContains(response, 'Enter your password')
    
    # test login user with unauthenticated user and post request and invalid username
    def test_login_user_using_post_request_and_invalid_username(self) :
        target_url = reverse('login')
        # define a username where length exceeds 20 characters
        data = {
            'username' : 'blablablablablablabla',
            'password' : 'test123'
        }
        response = self.client.post(target_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error_message'], "Username can not exceed 20 characters")
        # check for errror display 
        self.assertContains(response, "Username can not exceed 20 characters")
        self.assertContains(response, 'Enter your username')
        self.assertContains(response, 'Enter your password')
    
    # test with unauthenticated user using post request and valid data which corresponds to no user
    def test_login_user_using_post_request_and_credentials_corresponding_to_no_user(self) :
        data = {
            'username' : 'amine',
            'password' : 'test123'
        }
        target_url = reverse('login')
        response = self.client.post(target_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error_message'], 'Please check your credentials')
        self.assertContains(response, 'Enter your password')
        self.assertContains(response, 'Enter your username')
        self.assertContains(response, 'Please check your credentials')
    
    # test with unauthenticated user using post request and credentials corresponding to a user
    def test_login_user_using_post_request_and_credentials_corresponding_to_a_user(self):
        # create a user
        user = User.objects.create_user(username='amine', password='1234')
        target_url = reverse('login')
        data = { 'username' : 'amine', 'password' : '1234'}
        response = self.client.post(target_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        # check messages 
        my_messages = list(messages.get_messages(request=response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'success')
            self.assertEqual(message.message, 'Glad to see you again amine')
        # check that user is authenticated 
        self.assertTrue(user.is_authenticated)

# class to test the operation of registerUser View
class RegisterUserViewTests(TestCase) :
    # test registerUser with authenticated request
    def test_register_user_with_authenticated_user(self) :
        # create a user and authenticate him
        User.objects.create_user(username='amine', password='1234')
        self.client.login(username='amine', password='1234')
        target_url = reverse('register')
        # using get request
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        # using post request 
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
    
    # test registerUser with unauthenticated user using get request
    def test_register_user_with_unauthenticated_user_and_get_request(self) :
        target_url = reverse('register')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        form = CreateUserForm()
        self.assertIsInstance(response.context['form'], CreateUserForm)
        self.assertEqual(response.context['form'].initial, form.initial)
        # check for rendered html
        self.assertContains(response, 'Create an account Here')
        self.assertContains(response, 'Email Address')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')
        self.assertContains(response, 'Password confirmation')
    
    # test registerUser with unauthenticated user using post request and invalid form data
    def test_register_user_with_unauthenticated_user_using_post_request_and_invalid_data(self) :
        target_url = reverse('register')
        data = {
            'email' : 'test',
            'username' : 'amine',
            'password1' : 'amine123',
            'password2' : 'amine123'
        }
        response = self.client.post(target_url, data)
        self.assertEqual(response.status_code, 200)
        # check for form 
        self.assertEqual(response.context['form'].is_valid(), False)
        self.assertTrue(len(response.context['form'].errors) > 1)
        # check that email and password2 exist in form.errors dictionnary
        self.assertIn('email', response.context['form'].errors)
        self.assertIn('password2', response.context['form'].errors)
        # check for email error
        self.assertEqual(response.context['form'].errors['email'], ['Enter a valid email address.'])
        self.assertEqual(response.context['form'].errors['password2'], ['The password is too similar to the username.'])
        # check for errors in the rendered page 
        self.assertContains(response, 'The password is too similar to the username.')
        self.assertContains(response, 'Enter a valid email address.')
        # check that the form instance passed in context data is prefilled with submitted data
        self.assertEqual(response.context['form'].initial, CreateUserForm(data).initial)


    # test registerUser with post request and valid data
    @override_settings(EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend')
    def test_register_user_with_unauthenticated_user_using_post_request_and_valid_data(self) :
        target_url = reverse('register')
        data = {
            'email' : 'aminemaourid@gmail.com',
            'username' : 'amine',
            'password1' : 'anas1234',
            'password2' : 'anas1234'
        }
        response = self.client.post(target_url, data)
        
        # check for response status and redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        # check that a User instance has been created 
        self.assertTrue(User.objects.exists())
        self.assertEqual(User.objects.first().username, 'amine')
        # check that the user has been authenticated after successeful registration
        self.assertTrue(User.objects.get(username='amine').is_authenticated)
        # check that an email verification mail has been sent to the new user
        # assert the number of sent mails
        self.assertEqual(len(mail.outbox), 1)
        # check for mail attributes
        self.assertEqual(mail.outbox[0].subject, 'Email Verification')
        self.assertEqual(mail.outbox[0].to , ['aminemaourid@gmail.com'])
        self.assertEqual(mail.outbox[0].from_email, 'aminemaourid1@gmail.com')
        # check for html_message in the mail 
        html_message = None
        # iterate over the parts of the email message using walk
        for part in mail.outbox[0].message().walk() :
            if part.get_content_type() == 'text/html' :
                html_message = part.get_payload(decode=True).decode(part.get_content_charset())
                break
        self.assertIsNotNone(html_message)
        self.assertIn('Welcome to our community, Glad to have yet another member among us', html_message)
        self.assertIn('Please click the button to confirm your email Address', html_message)
        # check for EmailVerificationToken
        self.assertTrue(EmailVerificationToken.objects.exists())
        self.assertEqual(len(EmailVerificationToken.objects.all()), 1)
        self.assertEqual(EmailVerificationToken.objects.first().user, User.objects.get(username='amine'))
        # check that the new user email_verified attribute is False
        self.assertFalse(User.objects.get(username='amine').email_verified)
        # check for messages 
        my_messages = list(messages.get_messages(request=response.wsgi_request))
        self.assertEqual(len(my_messages), 2)
        self.assertCountEqual([message.tags for message in my_messages], ['success', 'info'])
    
# class to test operation of verify_email View 
class VerifyEmailViewTests(TestCase) :
        
    # test with unauthenticated user 
    def test_verify_email_with_unauthenticated_user(self) :
        # create a user 
        User.objects.create_user(username='amine', password='1234')
        target_url = reverse('verify_email')
        # using get request 
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
        # using post request 
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
    
    # test with authenticated user who already verified his email address and no query parameter
    def test_verify_email_with_authenticated_user_who_already_verified_his_email_and_no_query_parameter(self) :
        # first register a user , after registration a verification email token is emailed to the user
        user_data = {
            'username' : 'amine',
            'email' : 'amine@gmail.com',
            'password1' : 'af507890',
            'password2' : 'af507890'
        }
        registration_url = reverse('register')
        self.client.post(registration_url, user_data)
        # check that a user instance has been created 
        self.assertTrue(User.objects.exists())
        # check that an EmailVerificationToken is associated to the user just registered
        self.assertTrue(EmailVerificationToken.objects.filter(user=User.objects.get(username='amine')).exists())
        # check that the user is authenticated 
        self.assertTrue(User.objects.get(username='amine').is_authenticated)
        # build the url to verify email for the user 
        user_token = EmailVerificationToken.objects.get(user=User.objects.get(username='amine'))
        verification_url = f"{reverse('verify_email')}?token={user_token.token}"
        # perform get request to verification_url to simulate user verifying his email
        self.client.get(verification_url)
        # check that the email address has been verified 
        self.assertTrue(User.objects.get(username='amine').email_verified)
        # check the token has been deleted 
        self.assertFalse(EmailVerificationToken.objects.filter(user=User.objects.get(username='amine')).exists())
        # now that the user's email_verified is true send a request to 'verify_email' view
        target_url = reverse('verify_email')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_verified'])
        self.assertTrue(response.context['got_token_during_registration'])
        self.assertFalse(response.context['can_get_new_token'])
        self.assertEqual(response.context['email_address'],'amine@gmail.com')
        # check for rendered html
        self.assertContains(response, 'already verified')
        # send post request to target_url 
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_verified'])
        self.assertTrue(response.context['got_token_during_registration'])
        self.assertFalse(response.context['can_get_new_token'])
        self.assertEqual(response.context['email_address'],'amine@gmail.com')
        
    
    # test with authenticated user with email_verified attribute False and having an Expired email verification token
    def test_verify_email_with_authenticated_user_who_has_not_yet_verified_his_email_address_and_his_token_expired(self) :
        # register a user 
        user_data = {
            'username' : 'amine',
            'email' : 'amine@gmail.com',
            'password1' : 'af507890',
            'password2' : 'af507890'
        }
        registration_url = reverse('register')
        self.client.post(registration_url, user_data)
        # check that the user and an associated EmailVerificationToken have been created
        self.assertTrue(User.objects.filter(username='amine').exists())
        self.assertTrue(EmailVerificationToken.objects.filter(user=User.objects.get(username='amine')).exists())
        associated_token = EmailVerificationToken.objects.get(user=User.objects.get(username='amine'))
        # path the current time to be the token expires_at value, so we simulate the 1 hour passage
        # to get an expired token 
        with patch('django.utils.timezone.now') as mock_now :
            mock_now.return_value = associated_token.expires_at 
            target_url = reverse('verify_email')
            response = self.client.get(target_url)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context['is_verified'])
            self.assertTrue(response.context['can_get_new_token'])
            self.assertTrue(response.context['got_token_during_registration'])
            self.assertEqual(response.context['email_address'], 'amine@gmail.com')
            # check that the expired token has been deleted 
            self.assertFalse(EmailVerificationToken.objects.filter(user=User.objects.get(username='amine')).exists())
            self.assertContains(response, 'Your previous token has expired, get new One')
            self.assertContains(response, 'an Email with a verification Token will be sent to amine@gmail.com')
            self.assertContains(response, 'Get New One')
    
    # test verify_email with unauthenticated user who has not yet verified his email address and having a valid EmailVerificationToken
    def test_verify_email_with_authenticated_user_who_has_not_verified_his_email_yet_but_still_having_a_valid_token_after_registration(self) :
        # register a user 
        user_data =  {
            'username' : 'amine',
            'email' : 'amine@gmail.com',
            'password1' : 'af507890',
            'password2' : 'af507890'
        }
        registration_url = reverse('register')
        self.client.post(registration_url, user_data)
        # check that a user instance has been created 
        self.assertTrue(User.objects.exists())
        self.assertTrue(User.objects.filter(username='amine').exists())
        # check that an EmailVerificationToken has ben generated for the new user
        self.assertTrue(EmailVerificationToken.objects.filter(user=User.objects.get(username='amine')).exists())
        # get the associated token
        associated_token = EmailVerificationToken.objects.get(user=User.objects.get(username='amine'))
        # patch the current time to the token expiration date minus 1 second 
        with patch('django.utils.timezone.now') as mock_now :
            mock_now.return_value = associated_token.expires_at - timedelta(seconds=1)
            target_url = reverse('verify_email')
            response = self.client.get(target_url)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context['is_verified'])
            self.assertEqual(response.context['email_address'], 'amine@gmail.com')
            self.assertFalse(response.context['can_get_new_token'])
            self.assertTrue(response.context['got_token_during_registration'])
            # check for the response content
            self.assertContains(response, 'a valid Verification Token has been sent to :')
            self.assertContains(response, 'amine@gmail.com')
    
    # test with authenticated user with email not verified and has no EmailVerificationToken generated for him
    def test_verify_email_with_authenticated_user_having_unverified_email_and_no_email_verification_token(self) :
        # create a user and authenticate him 
        user = User.objects.create_user(username='amine', password='1234', email='amine@gmail.com')
        self.client.login(username='amine', password='1234')
        # check that email is not verified 
        self.assertFalse(user.email_verified)
        target_url = reverse('verify_email')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_verified'])
        self.assertEqual(response.context['email_address'], 'amine@gmail.com')
        self.assertTrue(response.context['can_get_new_token'])
        self.assertFalse(response.context['got_token_during_registration'])
        # check for response content 
        self.assertContains(response, 'Get a Token, to verify your Email Address')
        self.assertContains(response, 'an Email with a verification Token will be sent to')
        self.assertContains(response, 'Get New One')

    
    # the following tests are for the same url buth with a 'token' query parameter using get request

    # test with a valid token in query parameter but the token's user is not the authenticated user
    def test_verify_email_with_token_query_parameter_not_corresponding_to_the_authenticated_user(self) :
        # simulate registrating a user which generates a token for him and authenticates him
        # this user provides an email address not his
        user_data = {
            'username' : 'amine',
            'email' : 'test@gmail.com',
            'password1' : 'af507890',
            'password2' : 'af507890'
        }
        registartion_url = reverse('register')
        self.client.post(registartion_url, user_data)
        # check that a user has been created 
        self.assertTrue(User.objects.filter(username='amine').exists())
        # check that a token is associated to this user
        self.assertTrue(EmailVerificationToken.objects.exists())
        self.assertTrue(EmailVerificationToken.objects.filter(user=User.objects.get(username='amine')).exists())
        # get the token object created for the user after registration
        associated_token = EmailVerificationToken.objects.get(user=User.objects.get(username='amine'))
        # logout the user 
        self.client.logout()
        # extract the token value 
        token = associated_token.token 
        
        # create a user and authenticate him , this user is the owner of 'test@gmail.com'
        User.objects.create_user(username='test', password='12345', email='test@gmail.com')
        self.client.login(username='test', password='12345')
        # simulate the user clicking the button on the received email to check that the email belongs to him
        target_url = f"{reverse('verify_email')}?token={token}"
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        my_messages = list(messages.get_messages(request=response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'warning')
            self.assertEqual(message.message, 'Unauthorized action')
    
    # test with an EmailVerificationToken appended to url that doesn't exist no more because the user has already
    # verified his email address 
    def test_verify_email_with_token_query_parameter_after_already_verifying_his_email_address(self) :
        # simulate registering a user
        user_data = {
            'username' : 'amine',
            'email' : 'test@gmail.com',
            'password1' : 'af507890',
            'password2' : 'af507890'
        }
        registration_url = reverse('register')
        response = self.client.post(registration_url, user_data)
        self.assertTrue(User.objects.filter(username='amine').exists())
        self.assertTrue(EmailVerificationToken.objects.filter(user=User.objects.get(username='amine')).exists())
        # get the associated token 
        associated_token = EmailVerificationToken.objects.get(user=User.objects.get(username='amine'))
        token = associated_token.token 
        # build the url to which the user will be redirected after clicking the button on the received mail
        target_url = f"{reverse('verify_email')}?token={token}"
        # simulate the button click
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify_email'))
        # check that the user's email_verified is now true 
        self.assertTrue(User.objects.get(username='amine').email_verified)
        # check that the token has been deleted 
        self.assertFalse(EmailVerificationToken.objects.filter(token=token).exists())
        # simulate the user revisiting the mail and reclicking the button a second time
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify_email'))
        my_messages = list(messages.get_messages(request=response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'info')
            self.assertEqual(message.message, 'Email already verified')
    
    # test with an EmailVerificationToken appended to the url which is not valid 
    # the user passes a rendom string for example
    def test_verify_email_with_invalid_token_query_parameter(self) :
        # create a user and authenticate him
        User.objects.create_user(username='amine', password='1234', email='amine@gmail.com')
        self.client.login(username='amine', password='1234')
        random_token = 'sjfefkfe'
        target_url = f"{reverse('verify_email')}?token={random_token}"
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify_email'))
        my_messages = list(messages.get_messages(request=response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        for message in my_messages :
            self.assertEqual(message.tags, 'error')
            self.assertEqual(message.message, 'invalid Token')
    
    # test with an EmailVerificationToken appended to URL which has already expired 
    def test_verify_email_with_token_query_parameter_already_expired(self) :
        # register a user 
        user_data = {
            'username' : 'amine',
            'email' : 'test@gmail.com',
            'password1' : 'af507890',
            'password2' : 'af507890'
        }
        registration_url = reverse('register')
        response = self.client.post(registration_url, user_data)
        self.assertTrue(User.objects.exists())
        self.assertTrue(EmailVerificationToken.objects.filter(user=User.objects.get(username='amine')).exists())
        self.assertFalse(User.objects.get(username='amine').email_verified)
        self.assertTrue(User.objects.get(username='amine').is_authenticated)
        # get the associated token 
        associated_token = EmailVerificationToken.objects.get(user=User.objects.get(username='amine'))
        token = associated_token.token 
        # patch the current time to the token's expiration date 
        with patch('django.utils.timezone.now') as mock :
            mock.return_value = associated_token.expires_at
            target_url = f"{reverse('verify_email')}?token={token}"
            response = self.client.get(target_url)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('verify_email'))
            my_messages = list(messages.get_messages(request=response.wsgi_request))
            self.assertEqual(len(my_messages), 3)
            self.assertCountEqual([message.tags for message in my_messages], ['info', 'success', 'info'])
            self.assertCountEqual([message.message for message in my_messages], [
                'a verification email request was emailed to you, check your email to confirm your email',
                'Glad to have you amine, Enjoy our plateform',
                'Token expired'
            ])
    
    # test with an EmailVerificationToken appended to url which is still valid 
    def test_verify_email_with_token_query_parameter_still_valid(self) :
        # register a user 
        user_data = {
            'username' : 'amine',
            'email' : 'test@gmail.com',
            'password1' : 'af507890',
            'password2' : 'af507890'
        }
        registration_url = reverse('register')
        self.client.post(registration_url, user_data)
        self.assertTrue(User.objects.filter(username='amine').exists())
        self.assertTrue(EmailVerificationToken.objects.exists())
        associated_token = EmailVerificationToken.objects.get(user=User.objects.get(username='amine'))
        token = associated_token.token 
        self.assertFalse(User.objects.get(username='amine').email_verified)
        self.assertTrue(User.objects.get(username='amine').is_authenticated)
        self.client.logout()
        # reauthenticate the user
        self.client.login(username='amine', password='af507890')
        target_url = f"{reverse('verify_email')}?token={token}"
        # patch the current time to token's expiration date minus 1 second
        with patch('django.utils.timezone.now') as mock :
            mock.return_value = associated_token.expires_at - timedelta(seconds=1)
            response = self.client.get(target_url)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('verify_email'))
            # check that user's email_verified is now true
            self.assertTrue(User.objects.get(username='amine').email_verified)
            # check that the associated token is deleted 
            self.assertFalse(EmailVerificationToken.objects.filter(token=token).exists())
            # check for messages 
            my_messages = list(messages.get_messages(request=response.wsgi_request))
            self.assertEqual(len(my_messages), 1)
            message = my_messages[0]
            self.assertEqual(message.tags, 'success')
            self.assertEqual(message.message, 'Email verified successefully')
    
    # test verify_email using post request with user already verified his email address
    def test_verify_email_with_post_request_for_user_who_already_verified_his_email(self) :
        # register a user
        user_data = {
            'username' : 'amine',
            'email' : 'test@gmail.com',
            'password1' : 'af507890',
            'password2' : 'af507890'
        }
        registration_url = reverse('register')
        self.client.post(registration_url, user_data)
        self.assertTrue(User.objects.filter(username='amine').exists())
        self.assertTrue(EmailVerificationToken.objects.exists())
        self.assertFalse(User.objects.get(username='amine').email_verified)
        # get associated token
        associated_token = EmailVerificationToken.objects.get(user=User.objects.get(username='amine'))
        token = associated_token.token 
        # simulate clicking the button and setting the email to verified as a result
        target_url = f"{reverse('verify_email')}?token={token}"
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify_email'))
        # check that user's email_verified is true
        self.assertTrue(User.objects.get(username='amine').email_verified)
        # send a post request to 'verify_email' view
        response = self.client.post(reverse('verify_email'), {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_verified'])
        self.assertEqual(response.context['email_address'], 'test@gmail.com')
        self.assertFalse(response.context['can_get_new_token'], False)
        self.assertTrue(response.context['got_token_during_registration'])
        # check for rendered page content
        self.assertContains(response, 'already verified')
        self.assertContains(response, 'test@gmail.com')
        self.assertContains(response, "Email address already verified")
        my_messages = list(messages.get_messages(request=response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        message = my_messages[0]
        self.assertEqual(message.tags, 'info')
        self.assertEqual(message.message, 'Email address already verified')
    
    # test with post request for user not verified and doesn't have an EmailVerificationToken 
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_verify_email_with_post_request_for_user_not_verified_and_no_emailVerificationToken_associated(self):
        # create a user and authenticate him
        user = User.objects.create_user(username='amine', password='1234', email='amine@gmail.com')
        self.client.login(username='amine', password='1234')
        target_url = reverse('verify_email')
        # get request for verify_email view
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_verified'])
        self.assertEqual(response.context['email_address'], 'amine@gmail.com')
        self.assertTrue(response.context['can_get_new_token'])
        self.assertFalse(response.context['got_token_during_registration'])
        # check for rendered page content
        self.assertContains(response, 'Get a Token, to verify your Email Address')
        self.assertContains(response, 'an Email with a verification Token will be sent to amine@gmail.com')
        self.assertContains(response, 'Get New One')

        # simulate a post request to ask for a token 
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_verified'])
        self.assertEqual(response.context['email_address'], 'amine@gmail.com')
        self.assertFalse(response.context['can_get_new_token'])
        self.assertFalse(response.context['got_token_during_registration'])
        # check for rendered page content
        self.assertContains(response, 'a valid Verification Token has been sent to')
        self.assertContains(response, 'amine@gmail.com')
        # check for mail sending
        self.assertEqual(len(mail.outbox), 1)
        subject = 'Email Verification'
        from_email = 'aminemaourid1@gmail.com'
        recipient = ['amine@gmail.com']
        html_content = render_to_string('photoshare/verify_mail.html', 
                                        {'token' :EmailVerificationToken.objects.get(user=user).token})
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(mail.outbox[0].to, recipient)
        self.assertEqual(mail.outbox[0].from_email, from_email)
        self.assertEqual(mail.outbox[0].body, '')
        # check for html message sent , alternatives is a list where the 
        # first element is a tuple, where the first element is html message
        self.assertEqual(mail.outbox[0].alternatives[0][0], html_content)
        self.assertContains(response, 'a verification email request was emailed to you, check your email to confirm your email')
        # simulate a get request to verify_email view 
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_verified'])
        self.assertFalse(response.context['can_get_new_token'])
        self.assertContains(response, 'a valid Verification Token has been sent to :')
        self.assertContains(response, 'amine@gmail.com')
    
    # test with user already having a valid EmailVerificationToken and requesting a new one
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_verify_email_with_post_request_for_user_still_having_a_valid_token_and_requesting_another_one(self) :
        # register a user, this will create for him a token and mails him 
        user_data = {
            'username' : 'amine',
            'email' : 'test@gmail.com',
            'password1' : 'af507890',
            'password2' : 'af507890'
        }
        registration_url = reverse('register')
        self.client.post(registration_url, user_data)
        # check that a user has been created 
        self.assertTrue(User.objects.exists())
        # check that an EmailVerificationToken has been created and associate with the newly registred user
        self.assertTrue(EmailVerificationToken.objects.exists())
        self.assertTrue(EmailVerificationToken.objects.filter(user=User.objects.get(username='amine')).exists())
        # get the associated token 
        associated_token = EmailVerificationToken.objects.get(user=User.objects.get(username='amine'))
        token = associated_token.token
        # check that the user is authenticated and email_verified is false
        self.assertTrue(User.objects.get(username='amine').is_authenticated)
        self.assertFalse(User.objects.get(username='amine').email_verified)
        # check that an email has been sent to newly registred user
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject, 'Email Verification')
        self.assertEqual(sent_mail.body, '')
        self.assertEqual(sent_mail.to, ['test@gmail.com'])
        self.assertEqual(sent_mail.from_email, 'aminemaourid1@gmail.com')
        expected_html = render_to_string('photoshare/verify_mail.html', 
                                         {'token' : token})
        self.assertEqual(sent_mail.alternatives[0][0], expected_html)
        
        # send a get request to verify_email view
        target_url = reverse('verify_email')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_verified'])
        self.assertFalse(response.context['can_get_new_token'])
        self.assertTrue(response.context['got_token_during_registration'])
        self.assertContains(response,  'a valid Verification Token has been sent to :')
        self.assertContains(response, 'test@gmail.com')

        # now, test sending a post request to ask for an other EmailVerificationToken
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['email_address'], 'test@gmail.com')
        self.assertFalse(response.context['can_get_new_token'])
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        message = my_messages[0]
        self.assertEqual(message.tags, 'warning')
        self.assertEqual(message.message, "can't get a new Token, check your email")
        self.assertContains(response, "check your email")
    

    # test with post request for user who already has an EmailVerificationToken but it's expired
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_verify_email_with_post_request_for_user_with_email_verification_token_expired(self) :
        # register a user 
        user_data = {
            'username' : 'amine',
            'email' : 'test@gmail.com',
            'password1' : 'af507890',
            'password2' : 'af507890'
        }
        registration_url = reverse('register')
        self.client.post(registration_url, user_data)
        # check that the user has been created 
        self.assertTrue(User.objects.exists())
        # check that an EmailVerificationToken is associated to this user
        self.assertTrue(EmailVerificationToken.objects.filter(user=User.objects.get(username='amine')).exists())
        # check that a mail has been sent to the user 
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.to, ['test@gmail.com'])
        self.assertEqual(sent_mail.subject, 'Email Verification')
        # get the associated token
        associated_token = EmailVerificationToken.objects.get(user=User.objects.get(username='amine'))
        token = associated_token.token
        # patch the current moment to the token expiration date
        # get request for verify_email view 
        with patch('django.utils.timezone.now') as mock :
            mock.return_value = associated_token.expires_at
            target_url = reverse('verify_email')
            # send a get request 
            response = self.client.get(target_url)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context['is_verified'])
            self.assertTrue(response.context['can_get_new_token'])
            self.assertEqual(response.context['email_address'], 'test@gmail.com')
            self.assertContains(response, 'Your previous token has expired, get new One')
            # check that the Token has been deleted 
            self.assertFalse(EmailVerificationToken.objects.exists())
        # post request for verify_email view
        with patch('django.utils.timezone.now') as mock :
            mock.return_value = associated_token.expires_at 
            target_url = reverse('verify_email')
            # send a post request to get a new token 
            response = self.client.post(target_url, {})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['email_address'], 'test@gmail.com')
            self.assertEqual(response.context['can_get_new_token'], False)
            # check that the old token has been deleted 
            self.assertFalse(EmailVerificationToken.objects.filter(token=token).exists())
            self.assertEqual(EmailVerificationToken.objects.filter(user=User.objects.get(username='amine')).count(), 1)
            # check that an email has been sent to user 
            self.assertEqual(len(mail.outbox), 2)
            second_mail = mail.outbox[1]
            self.assertEqual(second_mail.subject, 'Email Verification')
            self.assertEqual(second_mail.to, ['test@gmail.com'])
            self.assertEqual(second_mail.body, '')
            self.assertEqual(second_mail.alternatives[0][0], render_to_string('photoshare/verify_mail.html', {'token' : EmailVerificationToken.objects.get(user=User.objects.get(username='amine')).token}))
            # check that a new Token has been created and mailed to the user 
            self.assertTrue(EmailVerificationToken.objects.filter(user=User.objects.get(username='amine')).exists())
            my_messages = list(messages.get_messages(response.wsgi_request))
            self.assertEqual(len(my_messages), 1)
            message = my_messages[0]
            self.assertEqual(message.tags, 'success')
            self.assertEqual(message.message, 'a verification email request was emailed to you, check your email to confirm your email')
            self.assertContains(response, 'a valid Verification Token has been sent to')
            self.assertContains(response, 'a verification email request was emailed to you, check your email to confirm your email')

# class to test the operation of addNew view 
class AddNewPhotoViewTests(TestCase) :
    # function that creates and authenticates a user
    def create_and_authenticate_a_user(self) :
        User.objects.create_user(username='amine', password='1234')
        self.client.login(username='amine', password='1234')

    # test with unauthenticated user 
    def test_add_new_photo_with_unauthenticated_user(self) :
        target_url = reverse('new')
        # target by using both get and post requests
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
        # the sent data dictionnary does't matter since the user is authenticated
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
    
    # test with authenticated user and get request
    def test_add_new_photo_with_authenticated_user_using_get_request(self) :
        self.create_and_authenticate_a_user()
        target_url = reverse('new')
        form = PhotoForm()
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        # check the form passed in context is empty 
        self.assertEqual(response.context['form'].initial, form.initial)
        self.assertContains(response, 'Add new Photo')
        self.assertContains(response, 'Save')
    
    # test with authenticated user and post request with invalid data 
    def test_add_new_photo_with_authenticated_user_using_post_request_and_invalid_data(self) :
        self.create_and_authenticate_a_user()
        # create a Category object
        my_category = Category.objects.create(name='sunset')
        # create a test file as an image 
        image_file = SimpleUploadedFile('test.jpg', b"content_file", 'image/jpeg')
        form_data = {
            'category' : my_category.id,
            'image' : image_file,
            'description' : ''
        }
        target_url = reverse('new')
        response = self.client.post(path=target_url, data=form_data)
        self.assertEqual(response.status_code, 200)
        form = PhotoForm(form_data)
        self.assertEqual(response.context['form'].initial, form.initial)
        # check that the form is invalid
        self.assertFalse(response.context['form'].is_valid())
        form_errors = []
        # typically, the image and description fields arent valid
        for field in response.context['form'].fields :
            # check if the field exists in the errors dictionnary
            if field in response.context['form'].errors :
                # get errors for each field , which is a list of all errors for the field
                form_errors.append(response.context['form'].errors[field])
        # check that all errors are printed 
        for error_list_for_field in form_errors :
            for error in error_list_for_field :
                self.assertContains(response, error)
        # i on purpose submitted the 'description' field empty while he's required
        # same thing the 'image' field doesn't contain a valid image 
        # i know that those fields will have errors, check the errors are printed
        for error in response.context['form'].errors['description'] :
            self.assertContains(response, error)
        for error in response.context['form'].errors['image'] :
            self.assertContains(response, error)

    # test with authenticated user using post request and valid data for the form
    def test_add_new_photo_with_authenticated_user_using_post_request_and_valid_data(self) :
        self.create_and_authenticate_a_user()
        # create a category Object
        mycategory = Category.objects.create(name='test')
        # create an image file 
        # get path to the test image file
        image_path = os.path.join(os.path.dirname(__file__), '../static/test/sunset.jpeg')
        # read the image_file and get it's binary data
        with open(image_path, 'rb') as f :
            image_data = f.read()
        image_file = SimpleUploadedFile('sunset.jpeg', image_data, 'image/jpeg')
        description = 'nice image for test'
        target_url = reverse('new')
        response = self.client.post(target_url, {
            'category' : mycategory.id,
            'image' : image_file,
            'description' : description})
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        message = my_messages[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, "Photo added with success ")
        # check that a Photo object has been created
        self.assertTrue(Photo.objects.exists())
        self.assertTrue(Photo.objects.filter(category=mycategory).exists())

# class to test the operation of delete photo view 
class DeletePhotoViewTests(TestCase) :
    def create_and_authenticate_a_user(self, is_superuser, username) :
        if is_superuser :
            user = User.objects.create_superuser(username='amine_super', password='12345')
            self.client.login(username='amine_super', password='12345')
            return user 
        
        user = User.objects.create_user(username=username, password='1234')
        self.client.login(username=username, password='1234')
        return user 
    
    # test with unauthenticated user 
    def test_dalete_photo_with_unauthenticated_user(self) :
        # build the target url and pass 1 as pk for photo to delete 
        target_url = reverse('delete', args=(1,))
        # test using get request
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
        # using POST request
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
    
    # test with authenticated user and unexisting Photo 
    def test_delete_photo_with_authenticated_user_for_unexisting_photo(self) :
        # create a user and authenticate him 
        self.create_and_authenticate_a_user(is_superuser=False, username='amine')
        # there's no Photo object, pass 1 as pk for the photo to delete
        target_url = reverse('delete', args=(1,))
        self.assertFalse(Photo.objects.exists())
        # target the view using get request
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'photoshare/404.html')
        # using post request
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'photoshare/404.html')
    
    # test with authenticated user trying to delete a Photo not his
    def test_delete_photo_with_authenticated_user_trying_to_delete_a_photo_not_his(self) :
        # create a regular user and authenticate him
        user = self.create_and_authenticate_a_user(is_superuser=False, username='amine')
        # create a category object to which the photo belongs
        my_category = Category.objects.create(name='sunset')
        # create a Photo object associated to the user 
        image_path = os.path.join(os.path.dirname(__file__),'../static/test/sunset.jpeg')    
        # read the image file and get binary data
        with open(image_path, 'rb') as f :
            image_data = f.read()
        image_file = SimpleUploadedFile('sunset.jpeg', image_data, 'image/jpeg')
        description = 'test image'
        Photo.objects.create(category=my_category, 
                            description=description, 
                            image=image_file,
                            created_by = user)
        self.client.logout()
        # check that a Photo object has been created 
        self.assertTrue(Photo.objects.exists())
        self.assertTrue(Photo.objects.filter(created_by=user).exists())
        self.assertEqual(Photo.objects.get(created_by=user).description, description)
        #  create an other regular user
        user2 = self.create_and_authenticate_a_user(is_superuser=False, username='anas')
        # build the url to delete the Photo created 
        target_url = reverse('delete', args=(Photo.objects.get(created_by=user).id,))
        # send a post request
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('detail_photo', args=(Photo.objects.get(created_by=user).id,)))
        my_messages = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        message = my_messages[0]
        self.assertEqual(message.tags, 'warning')
        self.assertEqual(message.message, 'Unauthorized action')
        # check that the Photo object still exists
        self.assertTrue(Photo.objects.filter(created_by=user).exists())
    
    # test with superuser authenticated trying to delete a photo that belongs to an other user
    def test_delete_photo_with_authenticated_user_deleting_a_photo_not_his(self) :
        # create a regular user and authenticate him
        user = self.create_and_authenticate_a_user(is_superuser=False, username='anas')
        # create a Photo object asssociated to the user 
        image_path = os.path.join(os.path.dirname(__file__), '../static/test/sunset.jpeg')
        with open(image_path, 'rb') as f :
            image_data = f.read()
        description = 'this photo belongs to anas'
        Photo.objects.create(
            category = Category.objects.create(name='sunset'),
            image = SimpleUploadedFile('sunset.jpeg', image_data, 'image/jpeg'),
            description = description,
            created_by = user
        )
        # check that a Photo object has been created and it's associated to anas
        self.assertTrue(Photo.objects.filter(created_by=user).exists())
        # logout the user 'anas'
        self.client.logout()
        # create and authenticate a superuser
        superuser = self.create_and_authenticate_a_user(is_superuser=True, username='amine')
        # the url to delete the Photo 
        target_url = reverse('delete', args=(Photo.objects.get(created_by=user).id,))
        # send a post request to delete 
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        my_messages = list(messages.get_messages(request=response.wsgi_request))
        self.assertEqual(len(my_messages), 1)
        message = my_messages[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(message.message, "Photo deleted with success !")
        # check that the Photo object has been deleted
        self.assertFalse(Photo.objects.exists())
        self.assertFalse(Photo.objects.filter(created_by=user).exists())
    

    # test with authenticated user deleting a photo that belongs to him
    def test_delete_photo_with_authenticated_user_deleting_his_photo(self) :
        # create a regular user and authenticate him
        user = self.create_and_authenticate_a_user(is_superuser=False, username='anas')
        # create a Photo object associated to the user 
        image_path = os.path.join(os.path.dirname(__file__), '../static/test/sunset.jpeg')
        with open(image_path, 'rb') as f :
            image_data = f.read()
        category = Category.objects.create(name='test_category')
        description = 'this is a test'
        Photo.objects.create(category = category,
                             image = SimpleUploadedFile('sunset.jpeg', image_data, 'image/jpeg'),
                             description = description,
                             created_by = user)
        # check that an object Photo is created for the user 
        self.assertTrue(user.photos.exists())
        self.assertEqual(user.photos.all().count(), 1)
        # build the url to target for delete
        target_url = reverse('delete', args=(Photo.objects.get(created_by=user).id,))
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gallery'))
        # check that photo has been deleted
        self.assertFalse(Photo.objects.exists())
        self.assertFalse(user.photos.exists())

# class to test the operation of editPhoto View 
class EditPhotoViewTests(TestCase) :
    # function that creates a user or a superuser, authenticate and renders him
    def create_and_authenticate_user(self, is_superuser, username) :
        if is_superuser :
            user = User.objects.create_superuser(username=username, password='1234')
            self.client.login(username=username, password='1234')
            return user 
        user = User.objects.create_user(username=username, password='enseirb')
        self.client.login(username=username, password='enseirb')
        return user 
    
    # test editPhoto with unauthenticated user
    def test_edit_photo_with_unauthenticated_user(self) :
        # build the target url 
        target_url = reverse('edit', args=(1,))
        # get request
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
        # post request
        response = self.client.post(target_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={target_url}")
        











    


















