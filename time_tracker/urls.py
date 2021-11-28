from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('all_tasks/', views.all_tasks, name='all_tasks'),
]