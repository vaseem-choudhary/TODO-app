from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Task
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm


# AUTH VIEWS

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)   
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful and logged in!')
            return redirect('task:task_list')   
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = RegistrationForm()

    return render(request, 'todo/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('task:task_list')   # fixed namespace
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'todo/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('task:login')   #  fixed namespace



# TASK VIEWS


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')  #  per-user tasks
    return render(request, 'todo/task_list.html', {'tasks': tasks})


@login_required
def task_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()

        if title:
            Task.objects.create(
                user=request.user,   #  assign task to user
                title=title,
                description=description
            )
            return redirect('task:task_list')

        error = "Title cannot be empty."
        return render(request, 'todo/task_form.html', {'error': error})

    return render(request, 'todo/task_form.html')


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)  #  user ownership check

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        completed = request.POST.get('completed') == 'on'

        if title:
            task.title = title
            task.description = description
            task.completed = completed
            task.save()
            return redirect('task:task_list')

        error = 'Title is required.'
        return render(request, 'todo/task_form.html', {
            'task': task,
            'error': error,
            'title_text': title,
            'desc_text': description,
            'completed': completed
        })

    return render(request, 'todo/task_form.html', {
        'task': task,
        'title_text': task.title,
        'desc_text': task.description,
        'completed': task.completed
    })


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)  #  user ownership check

    if request.method == 'POST':
        task.delete()
        return redirect('task:task_list')

    return render(request, 'todo/confirm_delete.html', {'task': task})


@login_required
def task_toggle_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)  #  user ownership check

    if request.method == 'POST':
        task.completed = not task.completed
        task.save()

    return redirect('task:task_list')
