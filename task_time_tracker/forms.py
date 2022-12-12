from django import forms
from django.forms import models
from django.contrib.auth.forms import (PasswordResetForm,
                                       UserCreationForm)

from .models import Project, Task, User

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
            'priority',
            'task_category',
            'task_notes',
            'expected_mins',
            'actual_mins',
        )
        labels = {
            'task_name': 'Name',
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
    
    def clean(self):
        """Check start_date against end_date"""
        super(NewProjectForm, self).clean()

        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        if start_date and end_date: 
            if start_date > end_date:
                self._errors['end_date'] = self.error_class([
                    'End date must come after start date'])
        
        return self.cleaned_data

class NewTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            'task_name',
            'task_notes',
            'expected_mins',
            'priority',
        )
        widgets = {
            'task_name': styles['short_input'],
            'task_notes': styles['long_input'],
            'expected_mins': styles['num_input'],
        }

class EditTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            'task_name',
            'priority',
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

class SitePasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='',
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )

class SiteUserCreationForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = (
            'username',
            'password1',
            'password2',
            'email',
        )