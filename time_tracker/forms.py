from.models import Task
from django import forms

class NewTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            'task_name',
            'task_category',
            'task_notes',
            'expected_mins',
        )