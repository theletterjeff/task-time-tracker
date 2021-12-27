from datetime import datetime

from django.db import models
from django.urls import reverse

class Task(models.Model):
    # Text values
    task_name = models.CharField(max_length=60)
    task_category = models.TextField(blank=True)
    task_notes = models.TextField(blank=True)

    # Completion durations
    expected_mins = models.IntegerField()
    actual_mins = models.IntegerField(null=True)

    # Completed yes/no
    completed = models.BooleanField(default=False)

    # Created/completed dates
    created_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True)

    # Status
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f'{self.id} "{self.task_name}" created on {self.created_date.strftime("%m/%d/%y")}'
    
    def edit_task_url(self):
        return reverse('edit_task', kwargs={'pk': self.id})
    
    def get_delete_task_url(self):
        return reverse('delete_task', kwargs={'pk': self.id})