from django.urls import path
# from . import views # No views needed here anymore for the web part handled in main urls.py

app_name = 'tasks'

# The web-specific URLs (create, update, delete) have been moved to the main task_manager/urls.py
# to match the template structure without requiring the 'tasks:' namespace prefix.
# API URLs are also defined in the main urls.py.
# This file can be kept empty or removed if no other app-specific URLs are needed.
urlpatterns = [
    # Add any other task-app-specific URLs here if necessary in the future.
    # For example, if you had a task-specific reporting page:
    # path('reports/', views.task_reports, name='task-reports'),
]