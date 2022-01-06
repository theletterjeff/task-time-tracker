from django_tables2 import Table, TemplateColumn

from .models import Task

dashboard_table_class = 'table table-striped table-hover table-sm'

class ActiveTaskTable(Table):
    """Note: must pass request argument to enable column sorting"""
    class Meta:
        model = Task
        fields = [
            'task_name',
            'expected_mins',
            'actual_mins',
            'completed',
        ]
        attrs = {'class': dashboard_table_class}
    
    edit = TemplateColumn(template_name='task_time_tracker/components/edit_button.html')

class AllTaskTable(Table):

    class Meta:
        model = Task
        exclude = ['id', 'active', 'created_date', 'completed_date']
        attrs = {'class': dashboard_table_class}
    
    edit = TemplateColumn(template_name='task_time_tracker/components/edit_button.html')

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