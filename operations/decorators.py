from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def is_admin(user):
    return (
        user.is_superuser
        or user.groups.filter(name='Admin').exists()
    )


def is_planner_or_admin(user):
    return (
        is_admin(user)
        or user.groups.filter(name='Planner').exists()
    )


def admin_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if is_admin(request.user):
            return view_func(request, *args, **kwargs)

        messages.error(
            request,
            'You do not have permission to perform this action.'
        )

        return redirect('dashboard')

    return wrapper


def planner_or_admin_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if is_planner_or_admin(request.user):
            return view_func(request, *args, **kwargs)

        messages.error(
            request,
            'You do not have permission to access this page.'
        )

        return redirect('dashboard')

    return wrapper