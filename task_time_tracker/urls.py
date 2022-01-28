from django.urls import include, path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('all_tasks/', views.all_tasks, name='all_tasks'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('inactive_tasks/', views.InactiveTaskView.as_view(), name='inactive_tasks'),
    path('delete-task/<int:pk>/', views.DeleteTaskView.as_view(), name='delete_task'),
    path('edit-task/<int:pk>/', views.EditTaskView.as_view(), name='edit_task'),
    path('todays-tasks/', views.TodaysTaskView.as_view(), name='todays_tasks'),
    path('new-task/', views.NewTaskView.as_view(), name='new_task'),
    path('new-project/', views.NewProjectView.as_view(), name='new_project'),
]

# User authentication
urlpatterns += [
    # Sign Up
    path('signup/', views.SignupView.as_view(), name='signup'),

    # Log in
    path('login/', views.SiteLoginView.as_view(), name='login'),
    path('logout/', views.SiteLogoutView.as_view(), name='logout'),

    # Change password
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    
    # Reset password
    path('password_reset/', views.SitePasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.SitePasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.SitePasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.SitePasswordResetCompleteView.as_view(), name='password_reset_complete'),
]