from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from bs4 import BeautifulSoup

from task_time_tracker.forms import SitePasswordResetForm
from task_time_tracker.models import User
from task_time_tracker.views import (SitePasswordResetConfirmView,
                                     SiteLoginView)

class LoginFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a user"""
        super().setUpClass()

        cls.credentials = {
            'username': 'username',
            'password': 'password',
        }

        cls.User = get_user_model()
        user = cls.User.objects.create_user(username=cls.credentials['username'])
        user.set_password(cls.credentials['password'])
        user.save()
    
    @classmethod
    def tearDownClass(cls):
        """Delete the user"""
        cls.User.objects.get(username=cls.credentials['username']).delete()
        super().tearDownClass()
    
    def setUp(self):
        """Log user in (if not already logged in)"""
        super(LoginFormTests, self).setUp()
        if '_auth_user_id' not in self.client.session:
            self.client.login(
                username=self.credentials['username'],
                password=self.credentials['password'],
            )

    def test_login_form_logs_user_in(self):
        """
        Submitting correct credentials to the login form logs the user in
        """
        credentials = {
            'username': 'username',
            'password': 'password',
        }
        form = SiteLoginView.form_class(data=credentials)
        self.assertTrue(form.is_valid())
    
    def test_login_form_with_incorrect_credentials_does_not_log_in_user(self):
        """
        Submitting incorrect credentials to the login form 
        does not log the user in
        """
        bad_credentials = {
            'username': 'nottherightlogin',
            'password': 'nottherightpassword'
        }
        form = SiteLoginView.form_class(data=bad_credentials)
        self.assertFalse(form.is_valid())

    def test_login_page_redirects_to_todays_tasks(self):
        """
        Submitting the login form redirects to the today's task page
        """
        response = self.client.post(
            reverse('login'),
            data=self.credentials,
            follow=True,
        )
        self.assertRedirects(response, reverse('todays_tasks'))
    
    def test_error_text_on_invalid_login(self):
        """
        Submitting incorrect credentials to the login form
        returns a page with error text on it
        """
        bad_credentials = {
            'username': 'nottherightlogin',
            'password': 'nottherightpassword'
        }
        response = self.client.post(
            reverse('login'),
            data=bad_credentials,
            follow=True,
        )
        soup = BeautifulSoup(response.content, 'html.parser')

        assert soup.find(id='sign-in-error')
    
    def test_correct_error_text_on_invalid_login(self):
        """
        Submitting incorrect credentials to the login form
        returns a page with correct error text on it
        """
        bad_credentials = {
            'username': 'nottherightlogin',
            'password': 'nottherightpassword'
        }
        response = self.client.post(
            reverse('login'),
            data=bad_credentials,
            follow=True,
        )
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual(
            soup.find(id='sign-in-error').text,
            'Sign in error. Please try again.'
        )


class PasswordResetRequestFormTests(TestCase):

    def test_blank_label_on_password_reset_form(self):
        """
        The label on the password reset form is equal to ''
        """
        form = SitePasswordResetForm
        self.assertEqual(form.declared_fields['email'].label, '')
    
class PasswordResetConfirmFormTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        credentials = {
            'username': 'passwordresetconfirmusername',
            'password': 'passwordresetconfirmpassword',
            'email': 'passwordresetconfirmemail@foo.com',
        }
        User = get_user_model()
        cls.user = User.objects.create_user(**credentials)

        return super().setUpClass()
    
    def test_correct_fields_in_password_reset_confirm_form(self):
        """
        The password reset confirm form includes the fields new_password1 and new_password2
        """
        form = SitePasswordResetConfirmView.form_class

        self.assertEqual(list(form.declared_fields.keys()), ['new_password1', 'new_password2'])
    
    def test_matching_passwords_make_form_valid(self):
        """
        Form is valid if new_password1 and new_password2 match
        """
        form = SitePasswordResetConfirmView.form_class
        data = {
            'new_password1': 'thisisapassword1234',
            'new_password2': 'thisisapassword1234',
        }
        self.assertTrue(form(user=self.user, data=data).is_valid())

    def test_different_passwords_make_form_invalid(self):
        """
        Form is invalid if new_password1 and new_password2 don't match
        """
        form = SitePasswordResetConfirmView.form_class
        data = {
            'new_password1': 'thisisapassword1234',
            'new_password2': 'adifferentpassword0987',
        }
        self.assertFalse(form(user=self.user, data=data).is_valid())