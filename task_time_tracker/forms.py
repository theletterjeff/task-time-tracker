from .models import Task
from django import forms

styles = {
    'short_input': forms.TextInput(attrs={'class': 'short-input'}),
    'long_input': forms.Textarea(attrs={'rows': '2'}),
    'num_input': forms.NumberInput(attrs={'class': 'short-input'}),
}

class NewTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            'task_name',
            'task_category',
            'task_notes',
            'expected_mins',
        )
        widgets = {
            'task_name': styles['short_input'],
            'task_category': styles['short_input'],
            'task_notes': styles['long_input'],
            'expected_mins': styles['num_input'],
        }

class UpdateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            'task_name',
            'task_category',
            'task_notes',
            'expected_mins',
            'actual_mins',
            'completed',
            'active',
        )
        widgets = {
            'task_name': styles['short_input'],
            'task_category': styles['short_input'],
            'task_notes': styles['long_input'],
        }