from datetime import datetime

from .models import Task

def deactivate_old_tasks():
    """Switches active status to inactive for tasks
    that weren't created today"""
    old_active_tasks = Task.objects.filter(
        active=True,
        # created_date.date() < datetime.today().date(),
    )