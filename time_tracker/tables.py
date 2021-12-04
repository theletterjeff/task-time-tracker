import django_tables2 as tables
from .models import Task

class InactiveTaskTable(tables.Table):
    class Meta:
        model = Task
        template_name = 'django_tables2/bootstrap.html'
        fields = (
                  'task_name',
                  'task_category',
                  'task_notes',
                  'expected_mins',
                  'created_date',
                  )