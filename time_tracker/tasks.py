import datetime

from .models import Task

def deactivate_old_tasks():
    """Switches active status to inactive for tasks
    that weren't created today. Uses django-q to run
    at midnight every day."""
    Task.objects.filter(
        active=True,
        created_date__date__lt=datetime.date.today(),
    ).update(active=False)