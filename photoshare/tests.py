from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from .models import PasswordResetToken
from django.urls import reverse
from django.core import mail
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

