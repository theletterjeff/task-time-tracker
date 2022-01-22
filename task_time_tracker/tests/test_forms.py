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
