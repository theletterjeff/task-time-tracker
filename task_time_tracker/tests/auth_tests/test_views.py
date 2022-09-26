from django.contrib.auth import get_user_model, get_user
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.test import tag, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from bs4 import BeautifulSoup
import pytest

from task_time_tracker.forms import SitePasswordResetForm

class LoginViewTests(TestCase):

    def setUp(self):
        self.response = self.client.get(reverse('login'))

    def test_view_url_exists_at_desired_location(self):
        abs_url_response = self.client.get('/login/')
        self.assertEqual(abs_url_response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        self.assertEqual(self.response.status_code, 200)

    def test_correct_login_template_used(self):
        """
        Calls to login URL return login template
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed('registration/login.html')

    def test_page_title_passed_in_context(self):
        """
        Context passed to LogInView includes page_title
        """
        assert self.response.context.get('page_title')
    
    def test_page_title_uses_correct_text(self):
        """
        Page title is 'Log In'
        """
        self.assertEqual(
            self.response.context['page_title'],
            'Log In'
        )

class PasswordResetViewTests(TestCase):

    def setUp(self):
        super(PasswordResetViewTests, self).setUp()
        
        # Create a new user
        User = get_user_model()
        credentials = {
            'username': 'test_submit_w_valid_email_username',
            'password': 'test_submit_w_valid_email_password',
            'email': 'test_submit_w_valid_email_emailaddress@foo.com',
        }
        User.objects.create_user(**credentials)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/password_reset/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        Password reset view uses the template
        'task_time_tracker/password_reset_form.html'
        """
        response = self.client.get(reverse('password_reset'))
        self.assertTemplateUsed(
            response,
            'task_time_tracker/password_reset_form.html'
        )
    
    def test_view_uses_correct_form(self):
        """
        Password reset view uses SitePasswordResetForm
        """
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.context['form'].__class__, SitePasswordResetForm)
    
    def test_page_title_in_context(self):
        """
        Page title appears in context
        """
        response = self.client.get(reverse('password_reset'))
        assert response.context['page_title']
    
    def test_page_title_uses_correct_text(self):
        """
        Page title is 'Reset Your Password'
        """
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.context['page_title'], 'Reset Your Password')
    
    def test_submit_w_valid_email_sends_email(self):
        """
        Submitting the password reset form after entering a valid
        email address sends an email prompt to the user
        """
        # Post password reset form
        self.client.post(
            reverse('password_reset'), 
            {'email': 'test_submit_w_valid_email_emailaddress@foo.com'},
            follow=True
        )
        self.assertEqual(len(mail.outbox), 1)

    def test_submit_wo_valid_email_does_not_send_email(self):
        """
        Submitting the password reset form after entering an invalid
        email address does not any email
        """
        self.client.post(
            reverse('password_reset'),
            {'email': 'abc@abc.com'},
            follow=True
        )
        self.assertEqual(len(mail.outbox), 0)
    
    @pytest.mark.xfail()
    def test_pw_reset_correct_subject_line(self):
        """
        Password reset email's subject line is
        'Reset Your Task Time Tracker Password'
        """
        self.client.post(
            reverse('password_reset'), 
            {'email': 'test_submit_w_valid_email_emailaddress@foo.com'},
            follow=True
        )
        self.assertEqual(len(mail.outbox), 1)
        
        subject_line = mail.outbox[0].subject
        self.assertEqual(subject_line, 'Reset Your Task Time Tracker Password')

class LogoutViewTests(TestCase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        Logout view uses the template
        'task_time_tracker/logout.html'
        """
        response = self.client.get(reverse('logout'))
        self.assertTemplateUsed(
            response,
            'task_time_tracker/logout.html'
        )
    
    def test_page_title_in_context(self):
        """
        Page title appears in context
        """
        response = self.client.get(reverse('logout'))
        assert response.context['page_title']
    
    def test_page_title_uses_correct_text(self):
        """
        Page title is 'Logged Out'
        """
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.context['page_title'], 'Logged Out')

    def test_link_to_login_uses_correct_url(self):
        """
        The link to the login page uses the URL for login
        """
        response = self.client.get(reverse('logout'))
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find login link, test URL
        login_link = soup.find(id='login-link')
        self.assertEqual(login_link.get('href'), reverse('login'))

class PasswordResetConfirmViewTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.credentials = {
            'username': 'passwordresetconfirmviewusername',
            'password': 'passwordresetconfirmviewpassword',
            'email': 'passwordresetconfirmviewemailaddress@foo.com',
        }
        cls.User = get_user_model()
        user = cls.User.objects.create_user(**cls.credentials)

        cls.token = PasswordResetTokenGenerator().make_token(user)
        cls.uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    @classmethod
    def tearDownClass(cls) -> None:
        """Delete user"""
        cls.User.objects.all().delete()
        super().tearDownClass()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(
            f'/reset/{self.uid}/{self.token}/',
            follow=True
        )
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        kwargs = {
            'uidb64': self.uid,
            'token': self.token,
        }
        response = self.client.get(reverse('password_reset_confirm', kwargs=kwargs), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        Password reset confirm view uses the template
        'task_time_tracker/password_reset_confirm.html'
        """
        kwargs = {
            'uidb64': self.uid,
            'token': self.token,
        }
        response = self.client.get(
            reverse('password_reset_confirm', kwargs=kwargs),
            follow=True
        )
        self.assertTemplateUsed(
            response,
            'task_time_tracker/password_reset_confirm.html'
        )
    
    def test_page_title_in_context(self):
        """
        Page title appears in context
        """
        kwargs = {
            'uidb64': self.uid,
            'token': self.token,
        }
        response = self.client.get(
            reverse('password_reset_confirm', kwargs=kwargs),
            follow=True
        )
        assert response.context['page_title']
    
    def test_page_title_uses_correct_text(self):
        """
        Page title is 'Reset Your Password'
        """
        kwargs = {
            'uidb64': self.uid,
            'token': self.token,
        }
        response = self.client.get(reverse('password_reset_confirm', kwargs=kwargs), follow=True)
        self.assertEqual(response.context['page_title'], 'Reset Your Password')

class PasswordResetDoneViewTests(TestCase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/password_reset/done/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        Password reset done view uses the template
        'task_time_tracker/password_reset_done.html'
        """
        response = self.client.get(reverse('password_reset_done'))
        self.assertTemplateUsed(
            response,
            'task_time_tracker/password_reset_done.html'
        )
    
    def test_page_title_in_context(self):
        """
        Page title appears in context
        """
        response = self.client.get(reverse('password_reset_done'))
        assert response.context['page_title']
    
    def test_page_title_uses_correct_text(self):
        """
        Page title is 'Password Reset Requested'
        """
        response = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response.context['page_title'], 'Password Reset Requested')

class PasswordResetCompleteViewTests(TestCase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/reset/done/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('password_reset_complete'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        Password reset complete view uses the template
        'task_time_tracker/password_reset_complete.html'
        """
        response = self.client.get(reverse('password_reset_complete'))
        self.assertTemplateUsed(
            response,
            'task_time_tracker/password_reset_complete.html'
        )
    
    def test_page_title_in_context(self):
        """
        Page title appears in context
        """
        response = self.client.get(reverse('password_reset_complete'))
        assert response.context['page_title']
    
    def test_page_title_uses_correct_text(self):
        """
        Page title is 'Password Reset Complete'
        """
        response = self.client.get(reverse('password_reset_complete'))
        self.assertEqual(response.context['page_title'], 'Password Reset Complete')

class SignupViewTests(TestCase):

    def test_view_url_exists_at_desired_location(self):
        """
        Requests to /signup/ should return status code 200
        """
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        Signup view uses the template 'task_time_tracker/signup.html'
        """
        response = self.client.get(reverse('signup'))
        self.assertTemplateUsed(
            response,
            'task_time_tracker/signup.html'
        )
    
    def test_page_title_in_context(self):
        """
        Page title appears in context
        """
        response = self.client.get(reverse('signup'))
        assert response.context['page_title']
    
    def test_page_title_uses_correct_text(self):
        """
        Page title is 'Password Reset Complete'
        """
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.context['page_title'], 'Sign Up')
    
    def test_base_template_logged_out_has_signup_link(self):
        """
        Page content for base template when user is logged out
        contains a link to sign up
        """
        # Make sure user isn't authenticated
        if get_user(self.client).is_authenticated:
            self.client.logout()

        response = self.client.get(reverse('dashboard'), follow=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        assert soup.find('a', string='Sign Up') 
    
    def test_posting_data_creates_new_user(self):
        """
        Submitting a POST request with new user data creates a new user
        """
        # Check to make sure there are no other users created
        User = get_user_model()
        self.assertEqual(len(User.objects.all()), 0)

        signup_credentials = {
            'username': 'username',
            'password1': 'atestpassword',
            'password2': 'atestpassword',
            'email': 'email@email.com',
        }
        self.client.post(
            reverse('signup'),
            data=signup_credentials,
        )
        assert User.objects.get(username='username')