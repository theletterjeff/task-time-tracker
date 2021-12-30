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

from .forms import NewTaskForm, UpdateTaskForm
from .models import Task
from .tables import ActiveTaskTable, InactiveTaskTable, CompletedTaskTable
from .utils.form_helpers import post_form_data, view_form
from .utils.model_helpers import DashboardSummStats, format_time

logger = logging.getLogger(__name__)

def dashboard(request):
    """Dashboard page for the time tracker.
    Includes new tasks, active tasks w/edit,
    and all tasks w/edit."""

    # Template path
    template = 'task_time_tracker/dashboard.html'

    # Set page title
    page_title = 'Dashboard'

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
    summ_stats = DashboardSummStats(active_tasks)

    estimated_time = format_time(summ_stats.estimated_time)
    estimated_plus_actual_time = format_time(summ_stats.estimated_plus_actual_time)
    actual_time = format_time(summ_stats.actual_time)
    unfinished_time = format_time(summ_stats.unfinished_time)


    # Assign variables
    context = {
        'page_title': page_title,
        'new_task_form': new_task_form,
        'active_task_table': active_task_table,
        'estimated_time': estimated_time,
        'estimated_plus_actual_time': estimated_plus_actual_time,
        'actual_time': actual_time,
        'unfinished_time': unfinished_time,
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
    template = 'task_time_tracker/index.html'
    return render(request, template)

class InactiveTaskListView(SingleTableView):
    model = Task
    table_class = InactiveTaskTable
    template_name = 'task_time_tracker/inactive_tasks.html'

def inactive_tasks(request):
    table = InactiveTaskTable(
        Task.objects.filter(active=False, completed=False)
    )
    return render(
        request,
        'task_time_tracker/inactive_tasks.html',
        {'table': table}
    )

class EditTaskView(UpdateView):
    model = Task
    form_class = UpdateTaskForm
    template_name = 'task_time_tracker/edit_task.html'
    context_object_name = 'task'

    extra_context = {'page_title': 'Edit Task'}

    def form_valid(self, form):
        task = form.save(commit=False)
        task.save()
        return redirect('dashboard')

class DeleteTaskView(DeleteView):
    model = Task
    success_url = reverse_lazy('dashboard')
    template_name = 'edit_task.html'
    context_object_name = 'task'