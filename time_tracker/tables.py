import django_tables2 as tables
from .models import Task

class BaseTaskTable(tables.Table):
    class Meta:
        template_name = 'django_tables2/bootstrap.html'

class ActiveTaskTable(BaseTaskTable):
    class Meta:
        model = Task
        fields = (
                  'task_name',
                  'task_category',
                  'task_notes',
                  'expected_mins',
                  'created_date',
                  )

class InactiveTaskTable(BaseTaskTable):
    class Meta:
        model = Task
        fields = (
                  'task_name',
                  'task_category',
                  'task_notes',
                  'expected_mins',
                  'created_date',
                  )

class CompletedTaskTable(BaseTaskTable):
    class Meta:
        model = Task
        exclude = (
                  'active',
                  'completed',
                  )