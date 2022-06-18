from tokenize import group
from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticaed_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:

            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorators(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, ** kwargs)

            else:
                return HttpResponse('you are not allowed')

        return wrapper_func
    return decorators


def admin_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name

        if group == 'firer':
            return redirect('profile')

        if group == 'admin':
            return view_func(request, *args, ** kwargs)

    return wrapper_function
