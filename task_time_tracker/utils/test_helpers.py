import datetime
import pytz

from lorem import get_word

from task_time_tracker.models import Task, Project, User

def create_user(username='username',
                password='testpassword',
                **kwargs):
    """Create a dummy user"""
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()

def get_user(user):
    """
    Return user if user is already created.
    If user is not already created, create and return user.
    """
    if user is None:
        if not User.objects.all():
            create_user()
        user = User.objects.get()
    
    return user

def create_task(task_name=get_word(count=2),
                expected_mins=1,
                user=None,
                **kwargs):
    """Create a dummy task"""
    user = get_user(user)

    return Task.objects.create(
        task_name=task_name,
        expected_mins=expected_mins,
        user=user,
        **kwargs,
    )

def create_project(name=get_word(count=2),
                   user=None,
                   **kwargs):
    """Create a dummy project"""
    user = get_user(user)
    
    return Project.objects.create(name=name,
                                  user=user,
                                  **kwargs)

def get_mocked_datetime():
    """Get a constant datetime object for use in mocked tests"""
    return datetime.datetime(
        2022, 1, 1, 0, 0, 0,
        tzinfo=pytz.timezone('America/New_York')
    )