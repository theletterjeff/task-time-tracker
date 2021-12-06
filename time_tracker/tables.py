import django_tables2 as tables
from .models import Task



class ActiveTaskTable(tables.Table):
    task_name = tables.Column(attrs={'td': {'class': 'odd-col'}})
    task_category = tables.Column(attrs={'td': {'class': 'even-col'}})
    task_notes = tables.Column(attrs={'td': {'class': 'odd-col'}})
    expected_mins = tables.Column(attrs={'td': {'class': 'even-col'}})
    created_date = tables.Column(attrs={'td': {'class': 'odd-col'}})

    class Meta:
        attrs = {'class': 'dashboard-task-table'}

class InactiveTaskTable(tables.Table):
    task_name = tables.Column(attrs={'td': {'class': 'odd-col'}})
    task_category = tables.Column(attrs={'td': {'class': 'even-col'}})
    task_notes = tables.Column(attrs={'td': {'class': 'odd-col'}})
    expected_mins = tables.Column(attrs={'td': {'class': 'even-col'}})
    created_date = tables.Column(attrs={'td': {'class': 'odd-col'}})

    class Meta:
        attrs = {'class': 'dashboard-task-table'}

class CompletedTaskTable(tables.Table):
    class Meta:
        model = Task
        exclude = (
                  'active',
                  'completed',
                  )