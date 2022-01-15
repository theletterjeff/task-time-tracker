from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Task, User

admin.site.register(Task)
admin.site.register(User, UserAdmin)