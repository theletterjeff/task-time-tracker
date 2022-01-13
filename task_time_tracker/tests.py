import datetime
import pytz
from time import sleep
from unittest import mock

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.paginator import EmptyPage
from django.test import Client, TestCase
from django.urls import reverse

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from lorem import get_word

from .exceptions import StartDateError
from .models import Task, Project, TaskStatusChange

def create_task(task_name=get_word(count=2),
                expected_mins=1,
                **kwargs):
    """Create a dummy task"""
    return Task.objects.create(
        task_name=task_name,
        expected_mins=expected_mins,
        **kwargs,
    )

def create_project(name=get_word(count=2),
                   **kwargs):
    """Create a dummy project"""
    return Project.objects.create(name=name,
                                  **kwargs)

def get_mocked_datetime():
    """Get a constant datetime object for use in mocked tests"""
    return datetime.datetime(
        2022, 1, 1, 0, 0, 0,
        tzinfo=pytz.timezone('America/New_York')
    )

class TaskModelTests(TestCase):

    def test_ordered_by_date_descending(self):
        """
        A queryset of newly created records is equal to
        the same queryset ordered by created_date descending
        """
        create_task(created_date=datetime.datetime.now())
        create_task(created_date=datetime.datetime.now() + datetime.timedelta(days=1))

        sorted_queryset_descending = Task.objects.all().order_by('-created_date')
        sorted_queryset_ascending = Task.objects.all().order_by('created_date')

        self.assertEqual(list(Task.objects.all()), list(sorted_queryset_descending))
        self.assertNotEqual(list(Task.objects.all()), list(sorted_queryset_ascending))
    
    def test_new_tasks_are_active(self):
        """
        The active property of newly created tasks is True
        """
        task = create_task()
        self.assertTrue(task.active)
    
    def test_new_task_priority_values_evaluate_correctly(self):
        """
        Creating tasks with priorities set to each of the four
        options (3, 2, 1, None <- default) return the correct
        values when calling priority property
        """
        task_high = create_task(priority=3)
        task_med = create_task(priority=2)
        task_low = create_task(priority=1)
        task_none = create_task()

        self.assertEqual(task_high.priority, 3)
        self.assertEqual(task_med.priority, 2)
        self.assertEqual(task_low.priority, 1)
        self.assertEqual(task_none.priority, None)
    
    def test_new_task_priority_labels_evaluate_correctly(self):
        """
        Creating tasks with priorities set to each of the four
        options (3, 2, 1, None <- default) return the correct
        labels when calling priority property
        """
        task_high = create_task(priority=3)
        task_med = create_task(priority=2)
        task_low = create_task(priority=1)
        task_none = create_task()

        self.assertEqual(task_high.get_priority_display(), 'High')
        self.assertEqual(task_med.get_priority_display(), 'Medium')
        self.assertEqual(task_low.get_priority_display(), 'Low')
        self.assertEqual(task_none.get_priority_display(), '--')
    
    def test_new_task_has_project_attribute(self):
        """
        Newly created tasks have an attribute called 'project'
        """
        task = create_task()
        project_attr = getattr(task, 'project', 'no attribute called project')
        self.assertNotEqual(project_attr, 'no attribute called project')
    
    def test_task_project_attr_equals_project_obj(self):
        """
        The project attribute of a task equals the project
        object that was assigned as the attribute
        """
        project = create_project()
        task = create_task(project=project)
        self.assertEqual(task.project, project)

class ProjectModelTests(TestCase):

    def test_new_project_created_date_now(self):
        """
        Default new project created_date is now.
        """
        mocked_datetime = get_mocked_datetime()
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=mocked_datetime)):
            project = create_project()
            self.assertEqual(project.created_date, mocked_datetime)
    
    def test_new_project_description_empty_string(self):
        """
        Newly created projects' default description
        attribute is equal to ''
        """
        project = create_project()
        self.assertEqual(project.description, '')

class TaskStatusChangeTests(TestCase):

    def test_task_active_status_change_creates_taskstatuschange_obj(self):
        """Changing a task's active property from False to True
        or from True to False creates a related TaskStatusChange object"""
        task_1 = create_task(active=False)
        task_1.active = True
        task_1.save()

        assert TaskStatusChange.objects.get(task=task_1)

        task_2 = create_task(active=True)
        task_2.active = False
        task_2.save()

        assert TaskStatusChange.objects.get(task=task_2)
    
    def test_completing_task_creates_taskstatuschange_obj(self):
        """
        Changing a task's completed property from False to True
        creates a related TaskStatusChange object
        """
        task = create_task(completed=False)
        task.completed = True
        task.save()

        assert TaskStatusChange.objects.get(task=task)

    def test_inactive_to_active_change_updates_active_datetime(self):
        """Changing a task's active property from False
        to True adds the current datetime to active_datetime
        field in TaskStatusChange model"""
        task = create_task(active=False)
        mocked_datetime = get_mocked_datetime()

        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=mocked_datetime)):
            task.active = True
            task.save()

            related_taskstatuschange_obj = TaskStatusChange.objects.get(task=task)
            
            self.assertEqual(
                related_taskstatuschange_obj.active_datetime,
                mocked_datetime
            )
    
    def test_inactive_to_active_change_updates_inactive_datetime(self):
        """Changing a task's active property from True
        to False adds the current datetime to inactive_datetime
        field in TaskStatusChange model"""
        task = create_task(active=True)
        mocked_datetime = get_mocked_datetime()

        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=mocked_datetime)):
            task.active = False
            task.save()

            related_taskstatuschange_obj = TaskStatusChange.objects.get(task=task)
            
            self.assertEqual(
                related_taskstatuschange_obj.inactive_datetime,
                mocked_datetime
            )


class TaskDashboardViewTests(TestCase):

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
        Note: there's an advanced way to do this with Selenium.
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

class SeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        options = Options()
        options.headless = True

        cls.driver = WebDriver(options=options)

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()
    
    ### Dashboard tests ###

    def test_todays_task_title_links_to_dedicated_page(self):
        """
        The card title for the "today's task" widget links to the
        standalone page for all of today's tasks.
        """
        self.driver.get('%s%s' % (self.live_server_url, reverse('dashboard')))
        todays_tasks_widget_title = self.driver.find_element_by_id('todays-task-widget-title')

        self.assertEqual(todays_tasks_widget_title.tag_name, 'a')

        link_url = todays_tasks_widget_title.get_attribute(name='href')

        self.assertEqual(
            link_url,
            self.live_server_url + reverse('todays_tasks')
        )
    
    def test_clicking_on_task_table_column_sorts(self):
        """
        Clicking on "Task name" column sorts data alphabetically.
        Clicking on it again sorts data reverse alphabetically.
        """
        create_task(task_name='task_2')
        create_task(task_name='task_4')
        create_task(task_name='task_1')
        create_task(task_name='task_3')

        self.driver.get('%s%s' % (self.live_server_url, reverse('dashboard')))
        task_name_header = self.driver.find_element_by_link_text('Task name')

        # First click--should appear ascending alphabetical
        task_name_header.click()
        task_name_objs = self.driver.find_elements_by_css_selector(
                '#active-task-table tr td:nth-of-type(1)')
        task_names = [obj.text for obj in task_name_objs]

        self.assertEqual(task_names, ['task_1', 'task_2', 'task_3', 'task_4'])

        #Second click--should appear descending alphabetical
        task_name_header = self.driver.find_element_by_link_text('Task name')
        task_name_header.click()

        task_name_objs = self.driver.find_elements_by_css_selector(
                '#active-task-table tr td:nth-of-type(1)')
        task_names = [obj.text for obj in task_name_objs]

        self.assertEqual(task_names, ['task_4', 'task_3', 'task_2', 'task_1'])
    
    def test_sidebar_links_display_in_right_order(self):
        """
        Sidebar items link to:
        - Dashboard
        - New Task
        - New Project
        - Today's Tasks
        """
        self.driver.get('%s%s' % (self.live_server_url, reverse('dashboard')))
        sidebar_link_elements = self.driver.find_elements_by_class_name('nav-link')
        
        # Actual URLs
        sidebar_urls = [element.get_property('href').replace(
                            self.live_server_url, '')
                         for element
                         in sidebar_link_elements]
        
        # Intended URLs
        url_names = [
            'dashboard',
            'new_task',
            'new_project',
            'todays_tasks',
            'inactive_tasks'
        ]
        intended_urls = [reverse(url_name)
                         for url_name
                         in url_names]

        # Test all intended URLs are in sidebar
        for idx, intended_url in enumerate(intended_urls):
            self.assertEqual(intended_url, sidebar_urls[idx])
        
        # Test all sidebar URLs are intended
        for idx, sidebar_url in enumerate(sidebar_urls):
            self.assertEqual(sidebar_url, intended_urls[idx])
        
        # Test text
        sidebar_texts = [element.text
                        for element
                        in sidebar_link_elements]
        intended_texts = [
            'Dashboard',
            'New Task',
            'New Project',
            "Today's Tasks",
            'Inactive Tasks',
        ]

        # Test all intended text is in sidebar
        for idx, intended_text in enumerate(intended_texts):
            self.assertEqual(intended_text, sidebar_texts[idx])
        
        # Test all sidebar text is intended
        for idx, sidebar_text in enumerate(sidebar_texts):
            self.assertEqual(sidebar_text, intended_texts[idx])
    
    ### New Project Tests ###

    def test_submit_new_project_form_creates_project(self):
        """
        Filling and submitting a project form creates a new project
        """
        self.driver.get('%s%s' % (self.live_server_url, reverse('new_project')))

        # Fields
        name_field = self.driver.find_element_by_id('id_name')
        desc_field = self.driver.find_element_by_id('id_description')
        start_field = self.driver.find_element_by_id('id_start_date')
        end_field = self.driver.find_element_by_id('id_end_date')

        # Add inputs
        name_field.send_keys('test_name')
        desc_field.send_keys('test_description')
        start_field.send_keys('1/1/2022')
        end_field.send_keys('12/31/2022')

        # Submit
        submit_button = self.driver.find_element_by_class_name('btn')
        submit_button.send_keys(Keys.RETURN)

        # Check that record was created
        sleep(1)
        assert Project.objects.filter(name='test_name')
    
    def test_submit_new_project_form_redirects_to_todays_tasks(self):
        """
        Filling and submitting a project redirects to the page for
        today's tasks
        """
        new_project_url = '%s%s' % (self.live_server_url, reverse('new_project'))
        self.driver.get(new_project_url)

        # Fill in required field
        name_field = self.driver.find_element_by_id('id_name')
        name_field.send_keys('test_name')

        # Submit
        submit_button = self.driver.find_element_by_class_name('btn')
        submit_button.send_keys(Keys.RETURN)

        # Wait until page redirects
        WebDriverWait(self.driver, 10).until(EC.url_changes(new_project_url))

        todays_tasks_url = '%s%s' % (self.live_server_url, reverse('todays_tasks'))
        self.assertEqual(self.driver.current_url, todays_tasks_url)

    def test_null_values_in_nullable_project_form_columns_accepted(self):
        raise Exception('to do')
    
    def test_non_date_value_in_date_fields_raises_exc_in_new_project(self):
        raise Exception('to do')
    
    def test_date_string_transformed_to_datetime_in_new_project(self):
        raise Exception('to do')
    
    def test_task_table_edit_button_redirects_to_todays_tasks(self):
        raise Exception('to do')

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

class EditTaskViewTests(TestCase):

    def test_correct_list_and_order_edit_task_form_fields(self):
        """
        Edit task form should contain the correct fields
        in the correct order
        """
        raise Exception('to do')

class NewProjectFormTests(TestCase):

    def test_new_project_start_date_after_end_date_raises_exc(self):
        """
        Creating a new project with a start date after the end
        date raises an exception
        """
        c = Client()
        post_data = {
            'name': get_word(2),
            'start_date': '1/1/2022',
            'end_date': '12/31/2021',
        }
        with self.assertRaises(StartDateError):
            c.post(reverse('new_project'), post_data)

class InactiveTasksViewTests(TestCase):

    def test_number_one(self):
        raise Exception('TBD, to do')