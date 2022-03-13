import datetime
from venv import create

from django.contrib.auth import get_user_model, get_user
from django.core.paginator import EmptyPage
from django.test import tag, TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from task_time_tracker.models import Project, Task, TaskStatusChange
from task_time_tracker.utils.test_helpers import create_task
import task_time_tracker.views as views

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
        """
        If there are no active tasks, the summary stats display as '0 mins'
        """
        # Get user, check they're logged in
        self.assertEqual(len(self.User.objects.all()), 1)
        user = self.User.objects.get()
        assert user.is_authenticated

        create_task(active=False, user=user)

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
        # Get user, check they're logged in
        self.assertEqual(len(self.User.objects.all()), 1)
        user = self.User.objects.get()
        assert user.is_authenticated

        create_task(user=user)
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
        # Get user, check they're logged in
        self.assertEqual(len(self.User.objects.all()), 1)
        user = self.User.objects.get()
        assert user.is_authenticated

        create_task(expected_mins=10, actual_mins=None, user=user) # 10
        create_task(expected_mins=10, actual_mins=5, user=user) # 10
        create_task(expected_mins=10, actual_mins=15, user=user) # 15

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['current_estimated_time'], '35 mins')
    
    def test_todays_tasks_paginates_after_ten_tasks(self):
        """
        Having more than 10 active tasks causes table to paginate.
        Note: there's an advanced way to make this happen with Selenium.
        For now, I'm going to simply test to see if the page is
        still valid when it has 'page=2' in the URL.
        """
        # Get user, check they're logged in
        self.assertEqual(len(self.User.objects.all()), 1)
        user = self.User.objects.get()
        assert user.is_authenticated

        # Create 10 tasks, which should not paginate the table
        for i in range(10):
            create_task(user=user)
        dashboard_url = reverse('dashboard')
        paginate_url = f'{dashboard_url}?page=2'

        with self.assertRaises(EmptyPage):
            self.client.get(paginate_url)

        # Create a 11th task, which should paginate the table
        create_task(user=user)
        response = self.client.get(paginate_url)
        self.assertEqual(response.status_code, 200)
    
    def test_time_spent_plus_remaining_equals_current_estimate(self):
        """
        Adding time spent and time remaining equals current time estimate.
        """
        # Get user, check they're logged in
        self.assertEqual(len(self.User.objects.all()), 1)
        user = self.User.objects.get()
        assert user.is_authenticated

        create_task(expected_mins=10, user=user)
        create_task(expected_mins=10, actual_mins=5, user=user)
        create_task(expected_mins=10, actual_mins=15, user=user)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(
            (response.context['summ_stats_obj'].actual_time +
             response.context['summ_stats_obj'].unfinished_time),
            35
        )
    
    def test_form_fields_on_create_new_task_form(self):
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
    
    def test_new_task_form_creates_task_for_logged_in_user(self):
        """
        Creating a new task with the dashboard page's new task form
        creates a new task for the logged in user.
        """
        # Check to make sure no other entries have carried over
        self.assertEqual(len(Task.objects.all()), 0)

        # Post a new task
        new_task_data = {
            'task_name': 'test task',
            'expected_mins': 10,
        }
        self.client.post(
            reverse('dashboard'),
            data=new_task_data,
        )

        # Get user (for equivalence testing)
        User = get_user_model()
        user = User.objects.get(username='username')
        
        self.assertEqual(Task.objects.get(task_name='test task').user, user)
    
    def test_get_todays_tasks_function_returns_correct_queryset(self):
        """
        The function `get_todays_tasks` from the views module
        returns active incomplete tasks regardless of creation date
        and active completed tasks if they were completed today
        (excluding those completed before today)
        """
        yesterday = timezone.now() - timezone.timedelta(days=1)

        task1 = create_task(active=True, completed=False)
        task2 = create_task(active=True, completed=False, created_date=yesterday)
        task3 = create_task(active=True, completed=True)
        task4 = create_task(active=True, completed=True)
        task5 = create_task(active=False, completed=False)
        task6 = create_task(active=False, completed=True)

        task3_status = TaskStatusChange.objects.create(
            task=task3,
            completed_datetime=timezone.now(),
        )
        task4_status = TaskStatusChange.objects.create(
            task=task4,
            completed_datetime=yesterday,
        )

        request_factory = RequestFactory()
        request = request_factory.get(reverse('dashboard'))
        request.user = self.User.objects.get()
        
        queryset = views.get_todays_tasks(request)

        # Include active tasks (incomplete & completed today)
        # irrespective of creation date
        self.assertIn(task1, queryset)
        self.assertIn(task2, queryset)
        self.assertIn(task3, queryset)

        # Exclude task that was completed before today
        self.assertNotIn(task4, queryset)

        # Exclude inactive tasks
        self.assertNotIn(task5, queryset)
        self.assertNotIn(task6, queryset)
        

class NewTaskViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a user"""
        super().setUpClass()

        cls.credentials = {
            'username': 'username',
            'password': 'password',
        }

        User = get_user_model()
        user = User.objects.create_user(
            username=cls.credentials['username'])
        user.set_password(cls.credentials['password'])
        user.save()
    
    @classmethod
    def tearDownClass(cls):
        """Delete the user"""
        User = get_user_model()
        User.objects.get(username='username').delete()

        super().tearDownClass()

    def setUp(self):
        """Log user in"""
        super(NewTaskViewTests, self).setUp()
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
    
    def test_post_data_to_url_creates_new_task(self):
        """
        Posting task_name and expected_mins data to the new_task
        URL creates a new task
        """
        new_task_data = {
            'task_name': 'test task',
            'expected_mins': 10,
        }
        self.client.post(
            reverse('new_task'),
            data=new_task_data,
        )
        assert Task.objects.get(task_name='test task')
    
    def test_create_new_task_adds_user_to_task(self):
        """
        Creating a new task assigns the logged in user as the
        foreign key 'user' on that task instance
        """
        # Check to make sure no other entries have carried over
        self.assertEqual(len(Task.objects.all()), 0)

        # Post a new task
        new_task_data = {
            'task_name': 'test task',
            'expected_mins': 10,
        }
        self.client.post(
            reverse('new_task'),
            data=new_task_data,
        )

        # Get user (for equivalence testing)
        User = get_user_model()
        user = User.objects.get(username='username')

        self.assertEqual(Task.objects.get(task_name='test task').user, user)

class NewProjectViewTests(TestCase):

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

    def test_new_project_page_load(self):
        """
        Response status for create project page load is 200
        """
        response = self.client.get(reverse('new_project'))
        self.assertEqual(response.status_code, 200)
    
    @tag('in_progress')
    def test_new_project_page_loads_correct_form_fields(self):
        """
        Form should include:

        - name (display as 'Name')
        - description (display as 'Description')
        - start_date (display as 'Start Date')
        - end_date (display as 'End Date')
        """
        response = self.client.get(reverse('new_project'))
        field_label_dict = {
            'name': 'Name',
            'description': 'Description',
            'start_date': 'Start Date',
            'end_date': 'End Date',
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
        
    def test_new_project_page_loads_fields_in_right_order(self):
        """
        New project page form fields are in the order:
        name, description, start_date, end_date
        """
        response = self.client.get(reverse('new_project'))
        fields = (
            'name',
            'description',
            'start_date',
            'end_date',
        )
        self.assertEqual(
            tuple(response.context['form'].fields.keys()), fields
        )
    
    def test_post_data_to_url_creates_new_project(self):
        """
        Posting name data to the new_project URL creates a new project
        """
        new_project_data = {
            'name': 'test project',
        }
        self.client.post(
            reverse('new_project'),
            data=new_project_data,
        )
        assert Project.objects.get(name='test project')
    
    def test_create_new_project_adds_user_to_project(self):
        """
        Creating a new task assigns the logged in user as the
        foreign key 'user' on that task instance
        """
        # Check to make sure no other entries have carried over
        self.assertEqual(len(Project.objects.all()), 0)

        new_project_data = {
            'name': 'test project',
        }
        self.client.post(
            reverse('new_project'),
            data=new_project_data,
        )

        # Get user (for equivalence testing)
        User = get_user_model()
        user = User.objects.get(username='username')

        self.assertEqual(Project.objects.get(name='test project').user, user)

class TodaysTasksViewTests(TestCase):

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

    def test_context_filled_w_active_tasks(self):
        """
        View contains active tasks and excludes inactive tasks.
        """
        # Get user
        self.assertEqual(len(self.User.objects.all()), 1)
        user = self.User.objects.get()

        # Set kwargs
        task_names = [f'task_{i}' for i in range(1, 5)]
        active_statuses = [True, True, False, False]
        completed_statuses = [False, True, False, True]

        data = list(zip(task_names, active_statuses, completed_statuses))
        param_names = ['task_name', 'active', 'completed']

        for i in range(4):

            # Zip a particular set up kwargs up with kwarg names
            kwargs = dict(zip(param_names, data[i]))

            # Add user to kwargs
            kwargs['user'] = user

            create_task(**kwargs)

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
    
    def test_todays_tasks_only_includes_tasks_from_logged_in_users(self):
        """
        The queryset for the today's task view does not
        include tasks from a user who is not logged in
        """
        # Get old user
        self.assertEqual(len(self.User.objects.all()), 1)
        user_1 = self.User.objects.get()

        # Create new user
        user_2 = self.User.objects.create(username='username_2')
        user_2.set_password('password_2')
        user_2.save()

        # Create a task for old and new user
        create_task(task_name='user1_task', user=user_1)
        create_task(task_name='user2_task', user=user_2)

        # Log out old user; log in new user
        self.client.logout()
        self.client.login(username='username_2', password='password_2')

        # Get queryset
        response = self.client.get(reverse('todays_tasks'))
        context_queryset = response.context['task_list']

        self.assertEqual(len(context_queryset), 1)

        task_names = [task.task_name for task in context_queryset]

        self.assertTrue('user2_task' in task_names)
        self.assertFalse('user1_task' in task_names)


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
        # Get user
        self.assertEqual(len(self.User.objects.all()), 1)
        user = self.User.objects.get()

        # Set kwargs
        task_names = [f'task_{i}' for i in range(1, 5)]
        active_statuses = [True, True, False, False]
        completed_statuses = [False, True, False, True]

        data = list(zip(task_names, active_statuses, completed_statuses))
        param_names = ['task_name', 'active', 'completed']

        for i in range(4):

            # Zip a particular set up kwargs up with kwarg names
            kwargs = dict(zip(param_names, data[i]))

            # Add user to kwargs
            kwargs['user'] = user

            create_task(**kwargs)

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

    def test_inactive_tasks_only_includes_tasks_from_logged_in_users(self):
        """
        The queryset for the inactive task view does not
        include tasks from a user who is not logged in
        """
        # Get old user
        self.assertEqual(len(self.User.objects.all()), 1)
        user_1 = self.User.objects.get()

        # Create new user
        user_2 = self.User.objects.create(username='username_2')
        user_2.set_password('password_2')
        user_2.save()

        # Create a task for old and new user
        create_task(task_name='user1_task', active=False, user=user_1)
        create_task(task_name='user2_task', active=False, user=user_2)

        # Log out old user; log in new user
        self.client.logout()
        self.client.login(username='username_2', password='password_2')

        # Get queryset
        response = self.client.get(reverse('inactive_tasks'))
        context_queryset = response.context['task_list']

        self.assertEqual(len(context_queryset), 1)

        task_names = [task.task_name for task in context_queryset]

        self.assertTrue('user2_task' in task_names)
        self.assertFalse('user1_task' in task_names)
