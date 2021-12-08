import django_tables2 as tables
from .models import Task

dashboard_table_class = 'table table-striped table-hover table-sm'

class ActiveTaskTable(tables.Table):

    class Meta:
        model = Task
        fields = [
            'task_name',
            'expected_mins',
            'actual_mins',
            'completed',
        ]
        attrs = {
            'class': dashboard_table_class,
        }

class InactiveTaskTable(tables.Table):

    class Meta:
        model = Task
        fields = [
            'task_name',
            'task_category',
            'task_notes',
            'expected_mins',
            'created_date',
        ]
        attrs = {'class': dashboard_table_class}

class CompletedTaskTable(tables.Table):
    class Meta:
        model = Task
        fields = [
            'task_name',
            'task_category',
            'task_notes',
            'expected_mins',
            'actual_mins',
            'created_date',
            'completed_date',
        ]
        attrs = {'class': dashboard_table_class}