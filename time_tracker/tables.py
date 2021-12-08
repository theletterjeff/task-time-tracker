import django_tables2 as tables
from .models import Task



class ActiveTaskTable(tables.Table):

    class Meta:
        model = Task
        fields = [
            'task_name',
            'task_category',
            'task_notes',
            'expected_mins',
            'actual_mins',
            'created_date',
        ]
        attrs = {
            'class': 'table table-striped table-hover table-sm',
            # 'style': 'width: 70%',
            # 'thead': {'class': 'thead-light'},
        }

class InactiveTaskTable(tables.Table):

    class Meta:
        model = Task
        attrs = {'class': 'table table-striped'}

class CompletedTaskTable(tables.Table):
    class Meta:
        model = Task
        exclude = (
                  'active',
                  'completed',
                  )