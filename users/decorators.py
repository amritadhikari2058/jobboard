from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from functools import wraps
from applications.models import Application


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


def job_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        job = kwargs.get("job")

        if not job:
            return redirect("job_list")

        if job.user != request.user:
            messages.error(request, "Only job owners can perform this action")
            return redirect("job_list")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def recruiter_owns_application(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        app_id = kwargs.get("app_id")
        application = get_object_or_404(Application, id=app_id)

        if application.job.user != request.user:
            messages.error(request, "You can only manage your own job applications")
            return redirect("job_list")

        kwargs["application"] = application
        return view_func(request, *args, **kwargs)

    return _wrapped_view
