from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Project, Task, TaskStatusChange, User

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(TaskStatusChange)
admin.site.register(User, UserAdmin)