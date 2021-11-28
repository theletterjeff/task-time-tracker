'''
logger
active tasks
other tasks (leading to all tasks page)
'''

from django.http import HttpResponse
from django.template import loader

from .models import Task

def dashboard(request):
    all_tasks = Task.objects.order_by('-created_date')
    # active_tasks = Task.objects.
    
    template = loader.get_template('time_tracker/dashboard.html')
    context = {}
    return HttpResponse(template.render(context, request))

def all_tasks(request):
    all_task_list = Task.objects.all()
    output = ', '.join([task.task_name for task in all_task_list])
    return HttpResponse(output)
