from datetime import datetime, timedelta
import logging

from django.contrib.auth import views as auth_views
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from django_tables2 import SingleTableView, RequestConfig

from .forms import NewProjectForm, NewTaskForm, NewTaskPageForm, UpdateTaskForm, SitePasswordResetForm
from .models import Project, Task
from .tables import ActiveTaskTable, AllTaskTable
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
    active_tasks = active_tasks.order_by('completed', '-expected_mins')
    active_task_table = ActiveTaskTable(active_tasks, request=request)
    active_task_table.paginate(
        page=request.GET.get('page', 1),
        per_page=6,
    )

    # New task form
    if request.method == 'POST':
        new_task_form = NewTaskForm(data=request.POST)
        if new_task_form.is_valid():
            new_task_form.save()
            reload_url = reverse('dashboard')
            return redirect(reload_url)
    else:
        new_task_form = NewTaskForm()

    # Summary stats
    summ_stats = DashboardSummStats(active_tasks)

    # initial_estimated_time = format_time(summ_stats.initial_estimated_time)
    current_estimated_time = format_time(summ_stats.current_estimated_time)
    actual_time = format_time(summ_stats.actual_time)
    unfinished_time = format_time(summ_stats.unfinished_time)


    # Assign variables
    context = {
        'page_title': page_title,
        'new_task_form': new_task_form,
        'active_task_table': active_task_table,
        'summ_stats_obj': summ_stats,
        'initial_estimated_time': format_time(summ_stats.initial_estimated_time),
        'current_estimated_time': current_estimated_time,
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

class NewTaskView(CreateView):
    model = Task
    form_class = NewTaskPageForm
    template_name = 'task_time_tracker/new-task.html'

    extra_context = {'page_title': 'Create a New Task'}

    def get_success_url(self):
        return reverse('todays_tasks')

class NewProjectView(CreateView):
    model = Project
    form_class = NewProjectForm
    template_name = 'task_time_tracker/new-project.html'

    extra_context = {'page_title': 'Start a New Project'}

    def get_success_url(self):
        return reverse('todays_tasks')

class EditTaskView(UpdateView):
    model = Task
    form_class = UpdateTaskForm
    template_name = 'task_time_tracker/edit_task.html'
    context_object_name = 'task'

    extra_context = {'page_title': 'Edit Task'}

    def form_valid(self, form):
        task = form.save(commit=False)
        task.save()
        return redirect('todays_tasks')

class DeleteTaskView(DeleteView):
    model = Task
    success_url = reverse_lazy('dashboard')
    template_name = 'edit_task.html'
    context_object_name = 'task'

class TodaysTaskView(SingleTableView):
    queryset = Task.objects.filter(active=True)
    queryset = queryset.order_by('completed', '-priority')

    template_name = 'task_time_tracker/todays-tasks.html'
    table_class = AllTaskTable

    extra_context = {'page_title': "Today's Tasks"}

class InactiveTaskView(SingleTableView):
    queryset = Task.objects.filter(active=False).filter(completed=False)
    queryset = queryset.order_by('-created_date', '-priority')

    template_name = 'task_time_tracker/todays-tasks.html'
    table_class = AllTaskTable

    extra_context = {'page_title': 'Inactive Tasks'}

# Authentication Views

class SiteLoginView(auth_views.LoginView):
    template_name = 'task_time_tracker/login.html'
    extra_context = {'page_title': 'Log In'}

class SiteLogoutView(auth_views.LogoutView):
    template_name = 'task_time_tracker/logout.html'
    extra_context = {'page_title': 'Logged Out'}

class SitePasswordResetView(auth_views.PasswordResetView):
    template_name= 'task_time_tracker/password_reset_form.html'
    form_class = SitePasswordResetForm
    extra_context = {'page_title': 'Reset Your Password'}

    email_template_name = 'task_time_tracker/password_reset_email.html'

class SitePasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'task_time_tracker/password_reset_confirm.html'
    extra_context = {'page_title': 'Reset Your Password'}