from functools import wraps
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from applications.models import Application


def recruiter_owns_application(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check recruiter
        if (
            not hasattr(request.user, "userrole")
            or request.user.userrole.role != "recruiter"
        ):
            messages.error(request, "Only recruiters can perform this action.")
            return redirect("job_list")

        application = kwargs.get("application")
        if not application:
            messages.error(request, "Application not found")
            return redirect("job_list")

        # Check ownership
        if application.job.user != request.user:
            messages.error(request, "You can only manage your own job applications.")
            return redirect("job_list")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def application_owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        application = Application.objects.get(id=kwargs.get("app_id"))
        is_owner = application.user == request.user
        is_recruiter = application.job.user == request.user

        if not (is_owner or is_recruiter):
            messages.error(request, "You are not allowed to view this application.")
            return redirect("job_list")

        return view_func(request, *args, **kwargs)

    return wrapper


def get_application(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        application = get_object_or_404(
            Application.objects.select_related("job", "user"), id=kwargs.get("app_id")
        )

        kwargs["application"] = application
        return view_func(request, *args, **kwargs)

    return wrapper
