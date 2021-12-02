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
        }