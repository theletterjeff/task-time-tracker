from time import sleep

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from task_time_tracker.models import Task, Project
from task_time_tracker.utils.test_helpers import create_task

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
    
    def test_task_edit_submit_redirects_to_todays_tasks(self):
        """
        Editing a task redirects to the page for today's tasks
        """
        # Create a dummy task
        create_task(task_name='task_1')

        # Get task id (for URL slug)
        task_pk = Task.objects.get(task_name='task_1').pk
        
        # Formulate URL for edit task
        edit_task_url = '%s%s' % (self.live_server_url,
                                  reverse('edit_task', kwargs={'pk': task_pk}))
        
        self.driver.get(edit_task_url)

        # Submit without edits
        submit_button = self.driver.find_element_by_class_name('btn')
        submit_button.send_keys(Keys.RETURN)

        # Wait until page redirects
        WebDriverWait(self.driver, 10).until(EC.url_changes(edit_task_url))

        todays_tasks_url = '%s%s' % (self.live_server_url, reverse('todays_tasks'))
        self.assertEqual(self.driver.current_url, todays_tasks_url)

    ### Log in tests ###

    def test_correct_page_title_appears_on_login_page(self):
        """
        The page title "Log In" appears on the login page
        """
        login_url = '%s%s' % (self.live_server_url, reverse('login'))
        self.driver.get(login_url)

        page_title = self.driver.find_element_by_id('page-title')
        self.assertEqual(page_title.text, 'Log In')
    
    def test_password_reset_link_loads_password_reset_page(self):
        """
        Clicking on the password reset link loads the password reset page
        """
        login_url = '%s%s' % (self.live_server_url, reverse('login'))
        self.driver.get(login_url)

        # Find, click password reset link
        pw_reset_link = self.driver.find_element_by_id('password-reset')
        pw_reset_link.click()

        # Wait until page redirects
        WebDriverWait(self.driver, 10).until(EC.url_changes(login_url))

        pw_reset_url = '%s%s' % (self.live_server_url, reverse('password_reset'))
        self.assertEqual(self.driver.current_url, pw_reset_url)