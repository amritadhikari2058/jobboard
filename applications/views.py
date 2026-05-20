from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from jobs.models import Job
from django.contrib.auth.decorators import login_required
from .services import ApplicationService
from users.decorators import normal_user_required, recruiter_required
from .decorators import application_owner_required, get_application
from applications.exceptions import ApplicationError
from applications.selectors import get_user_applications, get_job_applications
from .decorators import recruiter_owns_application
from .models import Application
from .forms import ApplicationForm, ApplicationLinkFormSet


@login_required
def application_list(request):
    status = request.GET.get("status")
    job_id = request.GET.get("job")

    applications = Application.objects.none()
    job = None
    
    if job_id:
        job = get_object_or_404(Job, id=job_id)

        applications = get_user_applications(job, status)
    return render(
        request, "applications/application_list.html", {"applications": applications}
    )


@login_required
@get_application
@application_owner_required
def application_detail(request, app_id, application):
    return render(
        request,
        "applications/application_detail.html",
        {
            "application": application,
            "previous_url": request.META.get("HTTP_REFERER", "/"),
        },
    )


@login_required
@get_application
@application_owner_required
def update(request, app_id, application):
    if request.method == "POST":
        resume = request.FILES.get("resume")
        application = ApplicationService.update_application(application, resume)

        messages.success(request, "Application updated successfully")

        return redirect("applications:application_list")
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
        return redirect("applications:application_list")

    return render(
        request, "applications/delete_application.html", {"application": application}
    )


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

    return redirect("applications:view_applicants", slug=application.job.slug)


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

    return redirect("applications:view_applicants", slug=application.job.slug)


@login_required
@recruiter_required
def view_applicants(request, slug):
    user = request.user
    job = get_object_or_404(Job, slug=slug, user=user)
    applications = get_job_applications(job)

    return render(
        request, "applications/view_applicants.html", {"applications": applications}
    )


@login_required
@recruiter_required
def applications_by_job(request):
    job_id = request.GET.get(job_id)
    applications = Application.objects.filter(job_id=job_id)
    return render(
        request, "applications/application_list.html", {"applications": applications}
    )


@login_required
def create(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        formset = ApplicationLinkFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            # Save main application first
            application = form.save(commit=False)
            application.user = request.user
            application.job = job
            application.save()

            # Attach formset to this application
            formset.instance = application
            formset.save()

            messages.success(request, "Application submitted successfully")
            return redirect("jobs:job_list")

    else:
        form = ApplicationForm()
        formset = ApplicationLinkFormSet()

    return render(
        request,
        "applications/apply_application.html",
        {
            "form": form,
            "formset": formset,
        },
    )


@login_required
@normal_user_required
def user_applications(request):
    applications = Application.objects.filter(user=request.user).select_related("job")
    status = request.GET.get("status")
    if status:
        applications = applications.filter(status=status)

    return render(
        request,
        "applications/user_applications.html",
        {
            "applications": applications,
        },
    )


@login_required
@recruiter_required
def recruiter_applications(request):
    jobs = Job.objects.filter(user=request.user).prefetch_related("applications")

    return render(
        request,
        "applications/recruiter_applications.html",
        {
            "jobs": jobs,
        },
    )


@login_required
@application_owner_required
def withdraw_application(request, app_id):
    application = get_object_or_404(Application, id=app_id)

    if application.user != request.user:
        messages.error(request, "Not allowed")

    if application.status != "pending":
        messages.warning(request, "Cannot withdraw after decision.")
        return redirect("applications:user_applications")

    if request.method == "POST":
        application.status = "withdrawn"
        application.save()
        messages.success(request, "Application withdrawn")

    messages.error(request, "Sorry, the application couldn't be withdrawn")
    return redirect("applications:user_applications")
