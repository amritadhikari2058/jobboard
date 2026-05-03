from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def recruiter_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        userrole = getattr(request.user, "userrole", None)

        if not userrole or userrole.role != "recruiter":
            messages.error(request, "Only recruiters can perform this action")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def normal_user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        userrole = getattr(request.user, "userrole", None)

        if not userrole or userrole.role != "normal_user":
            messages.error(request, "Only job seekers can perform this action")
            return redirect("job_list")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
