'''
logger
active tasks
other tasks (leading to all tasks page)
'''
from datetime import datetime
import logging
import pdb

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView

from django_tables2 import SingleTableView

from .forms import NewTaskForm
from .models import Task
from .tables import ActiveTaskTable, InactiveTaskTable, CompletedTaskTable

logger = logging.getLogger(__name__)

def dashboard(request):
    """Dashboard page for the time tracker.
    Includes new tasks, active tasks w/edit,
    and all tasks w/edit."""

    # Template path
    template = 'time_tracker/dashboard.html'

    # Read in task data (active, inactive, completed)
    active_tasks = Task.objects.filter(active=True, completed=False)
    inactive_tasks = Task.objects.filter(active=False, completed=False)
    completed_tasks = Task.objects.filter(completed=True)

    # New task form
    if request.method == 'POST':
        new_task_form = NewTaskForm(data=request.POST)

        if new_task_form.is_valid():
            new_task_form.save()
            reload_url = reverse('dashboard')
            return redirect(reload_url)

    else:
        new_task_form = NewTaskForm()

    # Assign variables
    context = {
        'new_task_form': new_task_form,
        'active_task_table': ActiveTaskTable(active_tasks),
        'inactive_task_table': InactiveTaskTable(inactive_tasks),
        'completed_task_table': CompletedTaskTable(completed_tasks),
    }
    return render(request, template, context)

def all_tasks(request):
    all_task_list = Task.objects.all()
    output = ', '.join([task.task_name for task in all_task_list])
    return HttpResponse(output)

def task_detail(request, task_id):
    task_str = get_object_or_404(Task, pk=task_id)
    return HttpResponse(f'Detail page for {task_str}.')

<<<<<<< HEAD
def index(request):
    template = 'time_tracker/index.html'
    return render(request, template)
=======
class InactiveTaskListView(SingleTableView):
    model = Task
    table_class = InactiveTaskTable
    template_name = 'time_tracker/inactive_tasks.html'

def inactive_tasks(request):
    table = InactiveTaskTable(
        Task.objects.filter(active=False, completed=False)
    )
    return render(
        request,
        'time_tracker/inactive_tasks.html',
        {'table': table}
    )
<<<<<<< HEAD
>>>>>>> 20858b8 (WIP inactive task page)
=======

def test(request):
    return render(request, 'time_tracker/test.html')
>>>>>>> 8b027ec (Bootstrap columns)
