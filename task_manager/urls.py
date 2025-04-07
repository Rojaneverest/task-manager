# task_manager/urls.py
"""
URL configuration for task_manager project.
"""
from django.contrib import admin
from django.urls import path, include
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
# Import views from the tasks app
from tasks import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # --- Web Interface URLs ---
    # Root path for displaying the task list (GET request) -> uses new task_list_view
    path('', views.task_list_view, name='web-task-list'),

    # Path for the reporting view
    path('report/', views.report_view, name='web-report'),

    # Path for handling the creation of a new task (POST request) -> uses views.task_create
    path('create/', views.task_create, name='web-task-create'), # Matches {% url 'web-task-create' %}

    # Path for handling the update of an existing task (POST request) -> uses views.task_update
    path('update/<int:pk>/', views.task_update, name='web-task-update'), # Matches {% url 'web-task-update' ... %}

    # Path for handling the deletion of an existing task (POST request) -> uses views.task_delete
    path('delete/<int:pk>/', views.task_delete, name='web-task-delete'), # Matches {% url 'web-task-delete' ... %}

    # Authentication URLs - Explicitly use our custom views
    path('login/', views.login_view, name='web-login'),
    path('register/', views.register_view, name='web-register'),
    path('logout/', views.logout_view, name='web-logout'),

    # --- Admin Site ---
    path('admin/', admin.site.urls),


    # --- API URLs (Map to the corresponding functions in tasks.views) ---
    # path('api/tasks/', views.api_task_list, name='api-task-list'),
    # path('api/tasks/create/', views.api_task_create, name='api-task-create'),
    # path('api/tasks/<int:pk>/', views.api_task_detail, name='api-task-detail'),
    # path('api/tasks/<int:pk>/update/', views.api_task_update, name='api-task-update'),
    # path('api/tasks/<int:pk>/delete/', views.api_task_delete, name='api-task-delete'),

    # path('api/users/', views.api_user_list, name='api-user-list'),
    # path('api/users/<int:pk>/', views.api_user_detail, name='api-user-detail'),

    # path('api/register/', views.UserRegistrationView.as_view(), name='api-register'),


    # --- DRF Auth & Schema ---
    # Includes login/logout views for browsable API and session auth (only for API)
    # path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI endpoint
    # path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

]

