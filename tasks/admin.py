from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'status', 'created_at')
    list_filter = ('status', 'date', 'user')
    search_fields = ('title', 'description')
    date_hierarchy = 'date'