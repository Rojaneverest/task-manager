# tasks/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required # Import Django's login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect # Removed unused HttpResponse
from rest_framework import status, permissions, generics # generics might not be used here directly
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.db.models import Q # Import Q for complex lookups
import datetime # Import datetime for date filtering
from rest_framework import serializers as drf_serializers # Import DRF serializers

from .models import Task
from .serializers import TaskSerializer, UserSerializer, UserRegistrationSerializer

# --- Web Views ---

@login_required
def task_list_view(request):
    """
    Handles GET requests to display the task list and the main page (index.html).
    This view corresponds to the URL named 'web-task-list'.
    """
    tasks = Task.objects.filter(user=request.user).order_by('date')
    context = {'tasks': tasks}
    # Assuming index.html is in 'tasks/templates/tasks/index.html' or similar APP_DIRS location
    return render(request, 'index.html', context)

@login_required
def task_create(request):
    """
    Handles POST requests to create a new task from the web form.
    """
    if request.method == 'POST':
        # Using serializer with request.POST - ensure form names match serializer fields
        serializer = TaskSerializer(data=request.POST)
        if serializer.is_valid():
            # Manually add user before saving
            serializer.save(user=request.user)
            return redirect('web-task-list')
        else:
            # Optional: Handle serializer errors if needed, e.g., re-render form with errors
            # For simplicity, just redirecting back
            print(serializer.errors) # Log errors for debugging
            return redirect('web-task-list') # Or render form again with errors
    # Redirect if not POST
    return redirect('web-task-list')

@login_required
def task_update(request, pk):
    """
    Handles POST requests to update an existing task from the web form.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        # Using serializer with request.POST
        serializer = TaskSerializer(task, data=request.POST, partial=True)
        if serializer.is_valid():
            serializer.save()
            return redirect('web-task-list')
        else:
            # Optional: Handle errors
            print(serializer.errors) # Log errors for debugging
            return redirect('web-task-list') # Or render form again with errors
    # Redirect if not POST
    return redirect('web-task-list')

@login_required
def task_delete(request, pk):
    """
    Handles POST requests to delete an existing task from the web form.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    # Should ideally only delete on POST request, but template uses POST form
    if request.method == 'POST':
        task.delete()
    # Always redirect back after attempting delete or if GET request
    return redirect('web-task-list')

@login_required
def report_view(request):
    """
    Handles GET requests to display the report page and filter tasks.
    """
    tasks = Task.objects.filter(user=request.user).order_by('date')

    # Get filter parameters from GET request
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    status_filter = request.GET.get('status')
    task_name_filter = request.GET.get('task_name')

    # Apply filters
    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            tasks = tasks.filter(date__gte=start_date)
        except ValueError:
            # Handle invalid date format if necessary
            pass
    if end_date_str:
        try:
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            tasks = tasks.filter(date__lte=end_date)
        except ValueError:
            # Handle invalid date format if necessary
            pass
    if status_filter and status_filter != 'all':
        tasks = tasks.filter(status=status_filter)
    if task_name_filter:
        tasks = tasks.filter(title__icontains=task_name_filter)

    context = {
        'tasks': tasks,
        'statuses': Task.STATUS_CHOICES, # Pass status choices to template
        'filters': request.GET # Pass current filters back to template to repopulate form
    }
    return render(request, 'report.html', context)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_task_list(request):
    """
    List all tasks for the authenticated user, with filtering options.
    """
    tasks = Task.objects.filter(user=request.user)

    status_filter = request.query_params.get('status', None)
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    search = request.query_params.get('search', None)
    if search:
        # Consider using Q objects for more complex searches if needed
        tasks = tasks.filter(title__icontains=search) | tasks.filter(description__icontains=search)

    ordering = request.query_params.get('ordering', '-date') # Default ordering if needed
    # Validate ordering fields if necessary
    valid_ordering_fields = ['title', '-title', 'date', '-date', 'status', '-status', 'created_at', '-created_at']
    if ordering in valid_ordering_fields:
         tasks = tasks.order_by(ordering)
    else:
        tasks = tasks.order_by('-date') # Apply default if invalid field given

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_task_create(request):
    """
    Create a new task for the authenticated user.
    """
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user) # Add user context here
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_task_detail(request, pk):
    """
    Retrieve a task by id, ensuring it belongs to the user.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    serializer = TaskSerializer(task)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def api_task_update(request, pk):
    """
    Update a task by id, ensuring it belongs to the user.
    Handles full update (PUT) or partial update (PATCH).
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)

    # Note: PUT should ideally require all fields, PATCH allows partial update.
    # Serializer handles this distinction with partial=True for PATCH.
    partial = request.method == 'PATCH'
    serializer = TaskSerializer(task, data=request.data, partial=partial)

    if serializer.is_valid():
        # User context is already part of the task object, no need to pass here
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def api_task_delete(request, pk):
    """
    Delete a task by id, ensuring it belongs to the user.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAdminUser]) # Correct permission class
def api_user_list(request):
    """
    List all users (admin only).
    """
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser]) # Correct permission class
def api_user_detail(request, pk):
    """
    Retrieve a user by id (admin only).
    """
    user = get_object_or_404(User, pk=pk)
    serializer = UserSerializer(user)
    return Response(serializer.data)


# Refactored api_register_user to Class-Based View for better schema generation
class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user.
    Provides endpoint for creating new user accounts.
    Requires username, password, and password confirmation.
    """
    queryset = User.objects.none() # Required for CreateAPIView, but we don't query existing users here.
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register New User",
        description="Creates a new user account. Requires username, password, and password confirmation.",
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(description="User registered successfully", response=drf_serializers.Serializer(data={"message": "User registered successfully"})), # Example response
            400: OpenApiResponse(description="Invalid input (e.g., passwords don't match, username taken)")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
             {"message": f"User '{user.username}' registered successfully"},
             status=status.HTTP_201_CREATED,
             headers=headers
         )
