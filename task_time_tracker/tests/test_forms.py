from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from lorem import get_word

from task_time_tracker.forms import EditTaskForm, NewProjectForm, SitePasswordResetForm
from task_time_tracker.views import SitePasswordResetConfirmView

class NewProjectFormTests(TestCase):

    def test_empty_new_project_form_is_invalid(self):
        """
        A completely empty new project form is invalid
        """
        form = NewProjectForm()
        self.assertFalse(form.is_valid())

    def test_new_project_form_with_only_name_specified_is_valid(self):
        """
        Creating a new project with only the name supplied is valid
        """
        form = NewProjectForm(data={'name': get_word(2)})
        self.assertTrue(form.is_valid())
    
    def test_new_project_form_start_date_after_end_date_is_invalid(self):
        """
        Creating a new project with a start date after the end date
        is deemed invalid
        """
        data = {
            'start_date': '1/1/2022',
            'end_date': '12/31/2021',
        }
        self.assertFalse(NewProjectForm(data=data).is_valid())
    
    def test_non_date_value_in_date_fields_is_invalid(self):
        """
        Submittting a non-date value in a date field raises an exception
        """
        test_vals = [
            'abc',
            '123',
            '*!%#',
        ]
        for val in test_vals:
            self.assertFalse(NewProjectForm(data={'start_date': val}).is_valid())

class EditTaskFormTests(TestCase):

    def test_correct_list_and_order_edit_task_form_fields(self):
        """
        Edit task form should contain the correct fields
        in the correct order
        """
        form = EditTaskForm
        intended_fields = (
            'task_name',
            'priority',
            'task_category',
            'task_notes',
            'expected_mins',
            'actual_mins',
            'completed',
            'active',
        )
        self.assertEqual(form._meta.fields, intended_fields)
    
class LoginFormTests(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'loginformusername',
            'password': 'loginformpassword',
        }
        User = get_user_model()
        User.objects.create_user(**self.credentials)

    def test_login_form_logs_user_in(self):
        """
        Submitting correct credentials to the login form logs the user in
        """
        self.assertTrue(self.client.login(**self.credentials))
    
    def test_login_form_with_incorrect_credentials_does_not_log_in_user(self):
        """
        Submitting incorrect credentials to the login form does not log the user in
        """
        bad_credentials = {'username': 'nottherightlogin', 'password': 'nottherightpassword'}
        self.assertFalse(self.client.login(**bad_credentials))

    def test_login_page_redirects_to_todays_tasks(self):
        """
        Submitting the login form redirects to the today's task page
        """
        response = self.client.post(reverse('login'), data=self.credentials, follow=True)
        self.assertRedirects(response, reverse('todays_tasks'))

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