from .models import Task
from django import forms

styles = {
    'short_input': forms.TextInput(attrs={'class': 'short-input'}),
    'long_input': forms.TextInput(attrs={'class': 'long-input'}),
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
            'expected_mins': styles['short_input'],
        }

class UpdateActiveForm(forms.ModelForm):
    """Integrate into active task table to enter actual minutes,
    mark as completed, and delete."""
    class Meta:
        model = Task
        fields = (
            'actual_mins',
            'completed',
        )
