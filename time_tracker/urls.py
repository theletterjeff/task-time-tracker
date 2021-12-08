from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('all_tasks/', views.all_tasks, name='all_tasks'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
<<<<<<< HEAD
<<<<<<< HEAD
    path('index/', views.index, name='index'),
=======
    path('inactive_tasks/', views.inactive_tasks, name='inactive_tasks')
>>>>>>> 20858b8 (WIP inactive task page)
=======
    path('inactive_tasks/', views.inactive_tasks, name='inactive_tasks'),
    path('test/', views.test, name='test'),
>>>>>>> 8b027ec (Bootstrap columns)
]