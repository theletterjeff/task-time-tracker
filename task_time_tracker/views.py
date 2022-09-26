from datetime import date, timedelta
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
from django.utils import timezone
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
from .tables import DashboardTaskTable, AllTaskTable, CompletedTaskTable
from .utils.model_helpers import DashboardSummStats, format_time

logger = logging.getLogger(__name__)

def get_todays_tasks(request):
    """
    Return active incomplete and complete tasks, excluding tasks that were
    completed before today.
    """
    return (Task.objects
                .filter(user=request.user)
                .filter(active=True)
                .exclude(completed_date__lt=timezone.now() - timedelta(days=1))
    )

def get_active_tasks(request):
    """Return active tasks that have not been completed."""
    return (Task.objects
                .filter(user=request.user)
                .filter(active=True)
                .exclude(completed=True)
    )

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
    todays_tasks = get_todays_tasks(request).order_by('completed', '-expected_mins')
    dashboard_task_table = DashboardTaskTable(todays_tasks, request=request)
    dashboard_task_table.paginate(
        page=request.GET.get('page', 1),
        per_page=10,
    )

    # New task form
    if request.method == 'POST':
        new_task_form = NewTaskForm(data=request.POST)
        new_task_form.instance.user = request.user
        if new_task_form.is_valid():
            new_task_form.save()
            reload_url = reverse('dashboard')
            return redirect(reload_url)
    else:
        new_task_form = NewTaskForm()

    # Summary stats
    summ_stats = DashboardSummStats(todays_tasks)

    # initial_estimated_time = format_time(summ_stats.initial_estimated_time)
    current_estimated_time = format_time(summ_stats.current_estimated_time)
    actual_time = format_time(summ_stats.actual_time)
    unfinished_time = format_time(summ_stats.unfinished_time)


    # Assign variables
    context = {
        'page_title': page_title,
        'new_task_form': new_task_form,
        'active_task_table': dashboard_task_table,
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

class NewTaskView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = NewTaskPageForm
    template_name = 'task_time_tracker/new-task.html'

    extra_context = {'page_title': 'New Task'}

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard')

class NewProjectView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = NewProjectForm
    template_name = 'task_time_tracker/new-project.html'

    extra_context = {'page_title': 'New Project'}

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard')

class EditTaskView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = EditTaskForm
    template_name = 'task_time_tracker/edit_task.html'
    context_object_name = 'task'

    extra_context = {'page_title': 'Edit Task'}

    def form_valid(self, form):
        task = form.save(commit=False)
        task.save()
        return redirect('dashboard')

class DeleteTaskView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('dashboard')
    context_object_name = 'task'

class ActiveTaskView(LoginRequiredMixin, SingleTableView):
    template_name = 'task_time_tracker/active-tasks.html'
    table_class = AllTaskTable

    extra_context = {'page_title': "Active Tasks"}

    def get_queryset(self):
        """Only show tasks created by logged-in user"""
        return get_active_tasks(self.request).order_by(
            'completed',
            '-priority',
        )

class CompletedTaskView(LoginRequiredMixin, SingleTableView):
    template_name = 'task_time_tracker/completed_tasks.html'
    table_class = CompletedTaskTable
    extra_context = {'page_title': 'Completed Tasks'}

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).filter(completed=True)


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