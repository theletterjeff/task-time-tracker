from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('all_tasks/', views.all_tasks, name='all_tasks'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('index/', views.index, name='index'),
    path('inactive_tasks/', views.inactive_tasks, name='inactive_tasks'),
    path('delete-task/<int:pk>/', views.DeleteTaskView.as_view(), name='delete_task'),
]