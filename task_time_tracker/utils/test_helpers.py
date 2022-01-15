import datetime
import pytz

from lorem import get_word

from task_time_tracker.models import Task, Project

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