from datetime import datetime, timedelta
import logging

from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from django_tables2 import SingleTableView, RequestConfig

from .forms import (NewProjectForm,
                    NewTaskForm,
                    NewTaskPageForm,
                    EditTaskForm,
                    SitePasswordResetForm,
                    SiteUserCreationForm)
from .models import Project, Task, User
from .tables import ActiveTaskTable, AllTaskTable
from .utils.model_helpers import DashboardSummStats, format_time

logger = logging.getLogger(__name__)

@login_required
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

class NewTaskView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = NewTaskPageForm
    template_name = 'task_time_tracker/new-task.html'

    extra_context = {'page_title': 'Create a New Task'}

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('todays_tasks')

class NewProjectView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = NewProjectForm
    template_name = 'task_time_tracker/new-project.html'

    extra_context = {'page_title': 'Start a New Project'}

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('todays_tasks')

class EditTaskView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = EditTaskForm
    template_name = 'task_time_tracker/edit_task.html'
    context_object_name = 'task'

    extra_context = {'page_title': 'Edit Task'}

    def form_valid(self, form):
        task = form.save(commit=False)
        task.save()
        return redirect('todays_tasks')

class DeleteTaskView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('dashboard')
    template_name = 'edit_task.html'
    context_object_name = 'task'

class TodaysTaskView(LoginRequiredMixin, SingleTableView):
    template_name = 'task_time_tracker/todays-tasks.html'
    table_class = AllTaskTable

    extra_context = {'page_title': "Today's Tasks"}

    def get_queryset(self):
        """Only show tasks created by logged-in user"""
        return Task.objects.filter(
                user=self.request.user
            ).filter(
                active=True
            ).order_by(
                'completed',
                '-priority'
            )

class InactiveTaskView(LoginRequiredMixin, SingleTableView):
    template_name = 'task_time_tracker/todays-tasks.html'
    table_class = AllTaskTable

    extra_context = {'page_title': 'Inactive Tasks'}

    def get_queryset(self):
        """Only show tasks created by logged-in user"""
        return Task.objects.filter(
                user=self.request.user
            ).filter(
                active=False
            ).filter(
                completed=False
            ).order_by(
                '-created_date',
                '-priority'
            )

# Authentication Views

class SiteLoginView(auth_views.LoginView):
    template_name = 'task_time_tracker/login.html'
    extra_context = {'page_title': 'Log In'}

class SiteLogoutView(auth_views.LogoutView):
    template_name = 'task_time_tracker/logout.html'
    extra_context = {'page_title': 'Logged Out'}

class SitePasswordResetView(auth_views.PasswordResetView):
    template_name = 'task_time_tracker/password_reset_form.html'
    form_class = SitePasswordResetForm
    extra_context = {'page_title': 'Reset Your Password'}

    email_template_name = 'task_time_tracker/password_reset_email.html'

class SitePasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'task_time_tracker/password_reset_done.html'
    extra_context = {'page_title': 'Password Reset Requested'}

class SitePasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'task_time_tracker/password_reset_confirm.html'
    extra_context = {'page_title': 'Reset Your Password'}

class SitePasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'task_time_tracker/password_reset_complete.html'
    extra_context = {'page_title': 'Password Reset Complete'}

class SignupView(SuccessMessageMixin, CreateView):
    """Create a new user"""
    model = User
    form_class = SiteUserCreationForm
    template_name = 'task_time_tracker/signup.html'

    success_url = reverse_lazy('login')
    success_message = 'Your profile was created successfully'

    extra_context = {'page_title': 'Sign Up'}