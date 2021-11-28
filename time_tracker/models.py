from django.db import models

class Task(models.Model):
    # Text values
    task_name = models.TextField()
    task_category = models.TextField(blank=True)
    task_notes = models.TextField(blank=True)

    # Completion durations
    expected_mins = models.IntegerField()
    actual_mins = models.IntegerField(null=True)

    # Completed yes/no
    completed = models.BooleanField(default=False)

    # Created/completed dates
    created_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True)

    # Status
    active = models.BooleanField(default=True)