# tasks/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect 
import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from .models import Task
from .forms import TaskForm
# from rest_framework import status, permissions, generics 
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
# from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
# from .serializers import TaskSerializer, UserSerializer, UserRegistrationSerializer
# from rest_framework import serializers as drf_serializers 
# from .serializers import TaskSerializer

@login_required
def task_list_view(request):
    """
    Handles GET requests to display the task list and the main page (index.html).
    This view corresponds to the URL named 'web-task-list'.
    """
    tasks = Task.objects.filter(user=request.user).order_by('date')
    context = {'tasks': tasks}
    return render(request, 'index.html', context)

@login_required
def task_create(request):
    """
    Handles POST requests to create a new task from the web form.
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            # Don't save to DB yet (commit=False)
            task = form.save(commit=False)
            # Set the user field
            task.user = request.user
            # Now save to DB
            task.save()
            return redirect('web-task-list')
        else:
            print(form.errors)
            return redirect('web-task-list')
    return redirect('web-task-list')

@login_required
def task_update(request, pk):
    """
    Handles POST requests to update an existing task from the web form.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('web-task-list')
        else:
            print(form.errors)
            return redirect('web-task-list')
    return redirect('web-task-list')

@login_required
def task_delete(request, pk):
    """
    Handles POST requests to delete an existing task from the web form.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
    return redirect('web-task-list')

@login_required
def report_view(request):
    """
    Handles GET requests to display the report page and filter tasks.
    """
    tasks = Task.objects.filter(user=request.user).order_by('date')

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    status_filter = request.GET.get('status')
    task_name_filter = request.GET.get('task_name')

    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            tasks = tasks.filter(date__gte=start_date)
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            tasks = tasks.filter(date__lte=end_date)
        except ValueError:
            pass
    if status_filter and status_filter != 'all':
        tasks = tasks.filter(status=status_filter)
    if task_name_filter:
        tasks = tasks.filter(title__icontains=task_name_filter)

    context = {
        'tasks': tasks,
        'statuses': Task.STATUS_CHOICES,
        'filters': request.GET
    }
    return render(request, 'report.html', context)


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('web-task-list') 
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    storage = messages.get_messages(request)
    for message in list(storage):
        if message.tags != 'error':
            storage.used = True
            
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to the next page or default to task list
                next_url = request.POST.get('next') or request.GET.get('next') or 'web-task-list'
                return redirect(next_url)
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    else:
        form = AuthenticationForm()
        next_url = request.GET.get('next')
    return render(request, 'login.html', {'form': form, 'next': next_url if 'next' in request.GET else None})

def logout_view(request):
    logout(request)
    return redirect('/login/')


# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# def api_task_list(request):
#     """
#     List all tasks for the authenticated user, with filtering options.
#     """
#     tasks = Task.objects.filter(user=request.user)
# 
#     status_filter = request.query_params.get('status', None)
#     if status_filter:
#         tasks = tasks.filter(status=status_filter)
# 
#     search = request.query_params.get('search', None)
#     if search:
#         tasks = tasks.filter(title__icontains=search) | tasks.filter(description__icontains=search)
# 
#     ordering = request.query_params.get('ordering', '-date') 
#     valid_ordering_fields = ['title', '-title', 'date', '-date', 'status', '-status', 'created_at', '-created_at']
#     if ordering in valid_ordering_fields:
#          tasks = tasks.order_by(ordering)
#     else:
#         tasks = tasks.order_by('-date') 
# 
#     serializer = TaskSerializer(tasks, many=True)
#     return Response(serializer.data)


# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def api_task_create(request):
#     """
#     Create a new task for the authenticated user.
#     """
#     serializer = TaskSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save(user=request.user) # Add user context here
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# def api_task_detail(request, pk):
#     """
#     Retrieve a task by id, ensuring it belongs to the user.
#     """
#     task = get_object_or_404(Task, pk=pk, user=request.user)
#     serializer = TaskSerializer(task)
#     return Response(serializer.data)


# @api_view(['PUT', 'PATCH'])
# @permission_classes([permissions.IsAuthenticated])
# def api_task_update(request, pk):
#     """
#     Update a task by id, ensuring it belongs to the user.
#     Handles full update (PUT) or partial update (PATCH).
#     """
#     task = get_object_or_404(Task, pk=pk, user=request.user)
# 
#     partial = request.method == 'PATCH'
#     serializer = TaskSerializer(task, data=request.data, partial=partial)
# 
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['DELETE'])
# @permission_classes([permissions.IsAuthenticated])
# def api_task_delete(request, pk):
#     """
#     Delete a task by id, ensuring it belongs to the user.
#     """
#     task = get_object_or_404(Task, pk=pk, user=request.user)
#     task.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET'])
# @permission_classes([IsAdminUser]) 
# def api_user_list(request):
#     """
#     List all users (admin only).
#     """
#     users = User.objects.all()
#     serializer = UserSerializer(users, many=True)
#     return Response(serializer.data)


# @api_view(['GET'])
# @permission_classes([IsAdminUser])
# def api_user_detail(request, pk):
#     """
#     Retrieve a user by id (admin only).
#     """
#     user = get_object_or_404(User, pk=pk)
#     serializer = UserSerializer(user)
#     return Response(serializer.data)


# class UserRegistrationView(generics.CreateAPIView):
#     """
#     Register a new user.
#     Provides endpoint for creating new user accounts.
#     Requires username, password, and password confirmation.
#     """
#     queryset = User.objects.none() 
#     serializer_class = UserRegistrationSerializer
#     permission_classes = [AllowAny]
# 
#     @extend_schema(
#         summary="Register New User",
#         description="Creates a new user account. Requires username, password, and password confirmation.",
#         request=UserRegistrationSerializer,
#         responses={
#             201: OpenApiResponse(description="User registered successfully", response=drf_serializers.Serializer(data={"message": "User registered successfully"})), # Example response
#             400: OpenApiResponse(description="Invalid input (e.g., passwords don't match, username taken)")
#         }
#     )
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         headers = self.get_success_headers(serializer.data)
#         return Response(
#              {"message": f"User '{user.username}' registered successfully"},
#              status=status.HTTP_201_CREATED,
#              headers=headers
#          )