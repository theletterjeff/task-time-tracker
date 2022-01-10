from .models import Project, Task
from django import forms

styles = {
    'short_input': forms.TextInput(attrs={'class': 'short-input'}),
    'long_input': forms.Textarea(attrs={'rows': '2'}),
    'num_input': forms.NumberInput(attrs={'class': 'short-input'}),
}

class NewTaskPageForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            'task_name',
            'project',
            'priority',
            'task_category',
            'task_notes',
            'expected_mins',
            'actual_mins',
        )
        labels = {
            'task_name': 'Name',
            'project': 'Project',
            'priority': 'Priority',
            'task_category': 'Categories',
            'task_notes': 'Notes/Description',
            'expected_mins': 'Expected Time (in Minutes)',
            'actual_mins': 'Time Spent So Far (in Minutes)',
        }

class NewProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            'name',
            'description',
            'start_date',
            'end_date',
        )

class NewTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            'task_name',
            'task_category',
            'task_notes',
            'expected_mins',
            'priority',
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