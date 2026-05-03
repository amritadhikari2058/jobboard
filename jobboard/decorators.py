from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from functools import wraps
from .models import Job


def job_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        job = get_object_or_404(Job, id=kwargs.get("id"))

        if not job:
            return redirect("job_list")

        if job.user != request.user:
            messages.error(request, "Only job owners can perform this action")
            return redirect("job_list")

        kwargs["job"] = job
        return view_func(request, *args, **kwargs)

    return _wrapped_view
