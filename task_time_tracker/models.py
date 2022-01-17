from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Meta:
        db_table = 'auth_user'

class TaskStatusChange(models.Model):
    
    task = models.ForeignKey('Task', on_delete=models.CASCADE)

    active_datetime = models.DateTimeField(blank=True, null=True)
    inactive_datetime = models.DateTimeField(blank=True, null=True)

    completed_datetime = models.DateTimeField(blank=True, null=True)

class Task(models.Model):

    # Text values
    task_name = models.CharField(max_length=60)
    task_category = models.TextField(blank=True)
    task_notes = models.TextField(blank=True)

    # Related project
    project = models.ForeignKey(
        'Project',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    # Completion durations
    expected_mins = models.IntegerField()
    actual_mins = models.IntegerField(null=True, blank=True)

    # Completed yes/no
    completed = models.BooleanField(default=False)

    # Created/completed dates
    created_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True)

    # Status
    active = models.BooleanField(default=True)

    # Priority
    class Priority(models.IntegerChoices):
        HIGH = 3, _('High')
        MEDIUM = 2, _('Medium')
        LOW = 1, _('Low')

        __empty__ = _('--')
    
    priority = models.IntegerField(
        choices=Priority.choices,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f'{self.id} "{self.task_name}" created on {self.created_date.strftime("%m/%d/%y")}'
    
    def __init__(self, *args, **kwargs):
        """Store old active values to see if they change"""
        super(Task, self).__init__(*args, **kwargs)
        self.old_active = self.active
        self.old_completed = self.completed
    
    def save(self, *args, **kwargs):
        """Create TaskActivity instance if active changes"""
        # Active
        if self.old_active == False and self.active == True:
            TaskStatusChange.objects.create(
                task=self,
                active_datetime=timezone.now(),
            )
        elif self.old_active == True and self.active == False:
            TaskStatusChange.objects.create(
                task=self,
                inactive_datetime=timezone.now(),
            )
        
        # Completed
        if self.old_completed == False and self.completed == True:
            TaskStatusChange.objects.create(
                task=self,
                completed_datetime=timezone.now(),
            )
        super(Task, self).save(*args, **kwargs)

    
    def edit_task_url(self):
        return reverse('edit_task', kwargs={'pk': self.id})
    
    def get_delete_task_url(self):
        return reverse('delete_task', kwargs={'pk': self.id})

class Project(models.Model):

    # Text values
    name = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True)

    # Auto date
    created_date = models.DateTimeField(auto_now_add=True)

    # User-created date
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.name