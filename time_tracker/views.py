from datetime import datetime, timedelta
import logging
import pdb

from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DeleteView
from django.views.generic.edit import UpdateView

from django_tables2 import SingleTableView

from .forms import NewTaskForm
from .models import Task
from .tables import ActiveTaskTable, InactiveTaskTable, CompletedTaskTable
from .utils.form_helpers import post_form_data, view_form

logger = logging.getLogger(__name__)

def dashboard(request):
    """Dashboard page for the time tracker.
    Includes new tasks, active tasks w/edit,
    and all tasks w/edit."""

    # Template path
    template = 'time_tracker/dashboard.html'

    # Read in task data, format table
    active_tasks = Task.objects.filter(active=True)
    active_task_table = ActiveTaskTable(active_tasks)
    active_task_table.paginate(
        page=request.GET.get('page', 1),
        per_page=6,
    )

    # New task form
    new_task_form = view_form(NewTaskForm, request)
    post_form_data(new_task_form)

    # Summary stats
    estimated_time = active_tasks.aggregate(Sum('expected_mins'))['expected_mins__sum']
    estimated_time_formatted = td_format(timedelta(minutes=estimated_time))

    

    actual_time = active_tasks.aggregate(Sum('actual_mins'))['actual_mins__sum']
    actual_time_formatted = td_format(timedelta(minutes=actual_time))

    # Assign variables
    context = {
        'new_task_form': new_task_form,
        'active_task_table': active_task_table,
        'estimated_time': estimated_time_formatted,
        'actual_time': actual_time_formatted,
    }
    return render(request, template, context)

def all_tasks(request):
    all_task_list = Task.objects.all()
    output = ', '.join([task.task_name for task in all_task_list])
    return HttpResponse(output)

def task_detail(request, task_id):
    task_str = get_object_or_404(Task, pk=task_id)
    return HttpResponse(f'Detail page for {task_str}.')

def index(request):
    template = 'time_tracker/index.html'
    return render(request, template)

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

def test(request):
    return render(request, 'time_tracker/test.html')

class EditTaskView(UpdateView):
    model = Task
    fields = (
        'task_name',
        'task_category',
        'task_notes',
        'expected_mins',
        'actual_mins',
        'completed',
        'active',
    )
    template_name = 'time_tracker/edit_task.html'
    context_object_name = 'task'

    def form_valid(self, form):
        task = form.save(commit=False)
        task.save()
        return redirect('dashboard')

class DeleteTaskView(DeleteView):
    model = Task
    success_url = reverse_lazy('dashboard')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)