from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('all_tasks/', views.all_tasks, name='all_tasks'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('index/', views.index, name='index'),
    path('inactive_tasks/', views.InactiveTaskView.as_view(), name='inactive_tasks'),
    path('delete-task/<int:pk>/', views.DeleteTaskView.as_view(), name='delete_task'),
    path('edit-task/<int:pk>/', views.EditTaskView.as_view(), name='edit_task'),
    path('todays-tasks/', views.TodaysTaskView.as_view(), name='todays_tasks'),
    path('new-task', views.NewTaskView.as_view(), name='new_task'),
    path('new-project', views.NewProjectView.as_view(), name='new_project'),
]