from django.contrib.auth import get_user_model, get_user
from django.core.paginator import EmptyPage
from django.test import TestCase
from django.urls import reverse

from task_time_tracker.utils.test_helpers import create_task

print('main view tests running')

class TaskDashboardViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a user"""
        super().setUpClass()

        cls.credentials = {
            'username': 'username',
            'password': 'password',
        }
        cls.User = get_user_model()
        cls.User.objects.create_user(**cls.credentials)
    
    @classmethod
    def tearDownClass(cls):
        """Delete the user"""
        cls.User.objects.get(
            username=cls.credentials['username']
        ).delete()

        super().tearDownClass()

    def setUp(self):
        """Log user in"""
        super().setUp()
        self.client.login(**self.credentials)

    def test_unauthenticated_user_redirects(self):
        """
        Unauthenticated users get redirected to the login view/template
        """
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_page_load(self):
        """Response status for page load is 200"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_no_tasks_summ_stats_show_zero(self):
        """If there are no tasks, tehs ummary stats display as '0 mins'"""
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['initial_estimated_time'], '0 mins')
        self.assertEqual(response.context['current_estimated_time'], '0 mins')
        self.assertEqual(response.context['actual_time'], '0 mins')
        self.assertEqual(response.context['unfinished_time'], '0 mins')
    
    def test_inactive_task_summ_stats_show_zero(self):
        """If there are no active tasks, the summary stats display as '0 mins'"""
        # Create an inactive task
        create_task(active=False)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['initial_estimated_time'], '0 mins')
        self.assertEqual(response.context['current_estimated_time'], '0 mins')
        self.assertEqual(response.context['actual_time'], '0 mins')
        self.assertEqual(response.context['unfinished_time'], '0 mins')
    
    def test_active_task_summ_stats_show_expected_mins(self):
        """
        If there is one active task with no actual time:
            - Initial/current estimated time is equal to the task's estimated time
            - Actual time is equal to '0 mins',
            - Time remaining is equal to the task's estimated time
        """
        create_task()
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['initial_estimated_time'], '1 min')
        self.assertEqual(response.context['current_estimated_time'], '1 min')
        self.assertEqual(response.context['actual_time'], '0 mins')
        self.assertEqual(response.context['unfinished_time'], '1 min')
    
    def test_current_estimate_uses_expected_mins_if_actual_lt(self):
        """
        current_estimated_time is calculated as the sum of expected_mins
        where actual_mins is less than expected_mins plus actual_mins
        where actual_mins is greater than expected_mins
        """
        create_task(expected_mins=10, actual_mins=None) # 10
        create_task(expected_mins=10, actual_mins=5) # 10
        create_task(expected_mins=10, actual_mins=15) # 15

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['current_estimated_time'], '35 mins')
    
    def test_todays_tasks_paginates_after_six_tasks(self):
        """
        Having more than 6 active tasks causes table to paginate.
        Note: there's an advanced way to make this happen with Selenium.
        For now, I'm going to simply test to see if the page is
        still valid when it has 'page=2' in the URL.
        """
        # Create 6 tasks, which should not paginate the table
        for i in range(6):
            create_task()
        dashboard_url = reverse('dashboard')
        paginate_url = f'{dashboard_url}?page=2'

        try:
            response = self.client.get(paginate_url)
        except EmptyPage:
            response = 'empty page'

        self.assertEqual(response, 'empty page')

        # Create a 7th task, which should paginate the table
        create_task()
        response = self.client.get(paginate_url)
        self.assertEqual(response.status_code, 200)
    
    def test_time_spent_plus_remaining_equals_current_estimate(self):
        """
        Adding time spent and time remaining equals current time estimate.
        """
        create_task(expected_mins=10)
        create_task(expected_mins=10, actual_mins=5)
        create_task(expected_mins=10, actual_mins=15)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(
            (response.context['summ_stats_obj'].actual_time +
             response.context['summ_stats_obj'].unfinished_time),
            35
        )
    
    def test_create_new_task_form_fields(self):
        """
        new_task_form's fields property is equal to
        ['task_name', 'task_category', 'task_notes',
        'expected_mins', 'priority]
        """
        included_fields = [
            'task_name',
            'task_category',
            'task_notes',
            'expected_mins',
            'priority',
        ]
        response = self.client.get(reverse('dashboard'))

        form_obj = response.context['new_task_form']
        form_fields = [field for field in form_obj.fields.keys()]
        
        self.assertEqual(form_fields, included_fields)

class NewTaskViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a user"""
        super().setUpClass()

        cls.credentials = {
            'username': 'username',
            'password': 'password',
        }
        cls.User = get_user_model()
        cls.User.objects.create_user(**cls.credentials)
    
    @classmethod
    def tearDownClass(cls):
        """Delete the user"""
        cls.User.objects.get(
            username=cls.credentials['username']
        ).delete()

        super().tearDownClass()

    def setUp(self):
        """Log user in"""
        super().setUp()
        self.client.login(**self.credentials)

    def test_new_task_page_load(self):
        """
        Response status for create task page load is 200
        """
        response = self.client.get(reverse('new_task'))
        self.assertEqual(response.status_code, 200)
    
    def test_new_task_page_loads_correct_form_fields(self):
        """
        Form should include:

        - task_name (display as "Name")
        - project (display as "Project")
        - task_category (display as "Categories")
        - task_notes (display as "Description/Notes")
        - expected_mins (display as "Expected Time (in Minutes)"
        - actual_mins (display as "Time Spent So Far (in Minutes)")
        - completed (display as "Already Complete?")
        - priority (display as "Priority")
        """
        response = self.client.get(reverse('new_task'))
        field_label_dict = {
            'task_name': 'Name',
            'project': 'Project',
            'priority': 'Priority',
            'task_category': 'Categories',
            'task_notes': 'Notes/Description',
            'expected_mins': 'Expected Time (in Minutes)',
            'actual_mins': 'Time Spent So Far (in Minutes)',
        }
        for field, label in field_label_dict.items():
            # Fields are correct
            self.assertIsNotNone(
                field, response.context['form'].fields.get(field)
            )
            # Labels are correct
            self.assertEqual(
                label, response.context['form'].fields.get(field).label
            )
        
    def test_new_task_page_loads_fields_in_right_order(self):
        """
        New task page form fields are in the order:
        task_name, project, priority, task_category,
        task_notes, expected_mins, actual_mins
        """
        response = self.client.get(reverse('new_task'))
        fields = (
            'task_name',
            'project',
            'priority',
            'task_category',
            'task_notes',
            'expected_mins',
            'actual_mins',
        )
        self.assertEqual(
            tuple(response.context['form'].fields.keys()), fields
        )

class TodaysTasksViewTests(TestCase):

    def test_context_filled_w_active_tasks(self):
        """
        View contains active tasks and excludes inactive tasks.
        """
        create_task(task_name='task_1', active=True, completed=False)
        create_task(task_name='task_2', active=True, completed=True)
        create_task(task_name='task_3', active=False, completed=False)
        create_task(task_name='task_4', active=False, completed=True)

        response = self.client.get(reverse('todays_tasks'))
        context_queryset = response.context['task_list']

        self.assertEqual(len(context_queryset), 2)
        
        task_names = [task.task_name for task in context_queryset]

        # Includes active tasks
        self.assertTrue('task_1' in task_names)
        self.assertTrue('task_2' in task_names)

        # Excludes inactive tasks
        self.assertTrue('task_3' not in task_names)
        self.assertTrue('task_4' not in task_names)

class InactiveTasksViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a user"""
        super().setUpClass()

        cls.credentials = {
            'username': 'username',
            'password': 'password',
        }
        cls.User = get_user_model()
        cls.User.objects.create_user(**cls.credentials)
    
    @classmethod
    def tearDownClass(cls):
        """Delete the user"""
        cls.User.objects.get(
            username=cls.credentials['username']
        ).delete()

        super().tearDownClass()

    def setUp(self):
        """Log user in"""
        super().setUp()
        self.client.login(**self.credentials)

    def test_context_filled_w_inactive_incomplete_tasks(self):
        """
        View contains inactive, incomplete tasks and excludes inactive tasks.
        """
        create_task(task_name='task_1', active=True, completed=False)
        create_task(task_name='task_2', active=True, completed=True)
        create_task(task_name='task_3', active=False, completed=False)
        create_task(task_name='task_4', active=False, completed=True)

        response = self.client.get(reverse('inactive_tasks'))
        context_queryset = response.context['task_list']

        self.assertEqual(len(context_queryset), 1)
        
        task_names = [task.task_name for task in context_queryset]

        # Includes inactive, incomplete tasks
        self.assertTrue('task_3' in task_names)

        # Excludes inactive tasks
        self.assertTrue('task_1' not in task_names)
        self.assertTrue('task_2' not in task_names)
        self.assertTrue('task_4' not in task_names)

