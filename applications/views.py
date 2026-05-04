from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Application
from jobboard.models import Job
from django.contrib.auth.decorators import login_required
from .services import ApplicationService
from users.decorators import (
    normal_user_required,
    recruiter_required,
    job_owner_required,
    recruiter_owns_application,
)
from .decorators import application_owner_required, get_application
from applications.exceptions import ApplicationError


@login_required
@normal_user_required
def application_list(request):
    applications = Application.objects.filter(user=request.user).select_related(
        "job", "user"
    )
    return render(
        request, "applications/application_list.html", {"applications": applications}
    )


@login_required
@get_application
@application_owner_required
def application_detail(request, app_id, application):
    return render(
        request, "applications/application_detail.html", {"application": application}
    )


@login_required
@get_application
@application_owner_required
def update(request, app_id, application):
    if request.method == "POST":
        resume = request.FILES.get("resume")
        application = ApplicationService.update_application(application, resume)

        messages.success(request, "Application updated successfully")

        return redirect("application_list")
    return render(
        request, "applications/update_application.html", {"application": application}
    )


@login_required
@get_application
@application_owner_required
def delete(request, app_id, application):
    if request.method == "POST":

        ApplicationService.delete_application(application, request.user)

        messages.success(request, "Application deleted successfully")
        return redirect("application_list")

    return render(
        request, "applications/delete_application.html", {"application": application}
    )


@login_required
@normal_user_required
def create(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        resume = request.FILES.get("resume")

        try:
            ApplicationService.apply(user=request.user, job=job, resume=resume)
            messages.success(request, "Application applied successfully!")

        except ApplicationError as e:
            messages.warning(request, str(e))

        return redirect("application_list")

    return render(request, "applications/apply_application.html", {"job": job})


@login_required
@get_application
@recruiter_owns_application
def accept_application(request, app_id, application):
    if request.method != "POST":
        return redirect("view_applicants", slug=application.job.slug)

    try:
        ApplicationService.update_application_status(
            application, request.user, "accepted"
        )
        messages.success(request, "Application accepted")
    except ApplicationError as e:
        messages.error(request, str(e))

    return redirect("view_applicants", slug=application.job.slug)


@login_required
@get_application
@recruiter_owns_application
def reject_application(request, app_id, application):
    if request.method != "POST":
        return redirect("view_applicants", slug=application.job.slug)

    try:
        ApplicationService.update_application_status(
            application, request.user, "rejected"
        )
        messages.success(request, "Application rejected")
    except ApplicationError as e:
        messages.error(request, str(e))

    return redirect("view_applicants", slug=application.job.slug)


@login_required
def view_applicants(request, slug):
    user = request.user

    if user.userrole.role != "recruiter":
        messages.info(request, "Only recruiters have access to the applicant's list")
        return redirect("job_list")

    job = get_object_or_404(Job, slug=slug, user=user)
    applications = Application.objects.filter(job=job).select_related("job", "user")

    return render(
        request, "jobboard/view_applicants.html", {"applications": applications}
    )
