import datetime
from unittest import mock

from django.test import TestCase

from task_time_tracker.models import Task, Project, TaskStatusChange
from task_time_tracker.utils.test_helpers import create_task, create_project, get_mocked_datetime

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

class TaskStatusChangeModelTests(TestCase):

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