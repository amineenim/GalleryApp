from datetime import timedelta
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from .models import PasswordResetToken
from django.urls import reverse
from django.core import mail
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.tokens import PasswordResetTokenGenerator
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





