'''
logger
active tasks
other tasks (leading to all tasks page)
'''
import pdb

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404

from .forms import NewTaskForm
from .models import Task

def dashboard(request, slug):
    """Dashboard page for the time tracker.
    Includes new tasks, active tasks w/edit,
    and all tasks w/edit."""

    # Task data (all and active)
    all_tasks = Task.objects.order_by('-created_date')
    active_tasks = [task for task in all_tasks if task.active == True]

    # Template
    template = loader.get_template('time_tracker/dashboard.html')
    context = {
        'all_tasks': all_tasks,
        'active_tasks': active_tasks,    
    }
    return HttpResponse(template.render(context, request))

def all_tasks(request):
    all_task_list = Task.objects.all()
    output = ', '.join([task.task_name for task in all_task_list])
    return HttpResponse(output)
