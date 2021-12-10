from django_tables2 import Table, TemplateColumn

from .models import Task

dashboard_table_class = 'table table-striped table-hover table-sm'

class ActiveTaskTable(Table):

    class Meta:
        model = Task
        fields = [
            'task_name',
            'expected_mins',
            'enter_actual_mins',
            'mark_as_completed',
        ]
        attrs = {
            'class': dashboard_table_class,
        }
    
    enter_actual_mins = TemplateColumn(template_name='time_tracker/components/tables/enter_actual_mins.html')
    mark_as_completed = TemplateColumn(template_name='time_tracker/components/tables/mark_as_completed.html')


class InactiveTaskTable(Table):

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

class CompletedTaskTable(Table):
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