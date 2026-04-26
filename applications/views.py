from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Application
from jobboard.models import Job
from django.contrib.auth.decorators import login_required
from jobboard.utils import log_activity


@login_required
def application_list(request):
    applications = Application.objects.filter(user=request.user)
    return render(
        request, "applications/application_list.html", {"applications": applications}
    )


@login_required
def application_detail(request, app_id):
    application = get_object_or_404(Application, id=app_id, user=request.user)
    return render(
        request, "applications/application_detail.html", {"application": application}
    )


@login_required
def update(request, app_id):
    application = get_object_or_404(Application, id=app_id, user=request.user)
    if request.method == "POST":
        application.resume = request.FILES.get("resume")
        application.status = request.POST.get("status")
        application.save()
        return redirect("application_list")
    return render(
        request, "applications/update_application.html", {"application": application}
    )


@login_required
def delete(request, app_id):
    application = get_object_or_404(Application, id=app_id, user=request.user)
    if request.method == "POST":
        application.delete()
        return redirect("application_list")
    return render(
        request, "applications/delete_application.html", {"application": application}
    )


@login_required
def create(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    existing = Application.objects.filter(job=job, user=request.user).first()

    if existing:
        messages.warning(request, "You have already applied for this job.")
        return redirect("application_list")

    if request.method == "POST":
        resume = request.FILES.get("resume")

        application = Application.objects.create(
            job=job, user=request.user, resume=resume
        )

        log_activity(
            user=request.user,
            action_type="application_created",
            message=f"Applied to '{job.title}'",
            job=job,
            application=application,
        )
        messages.success(request, "Application applied successfully!")
        return redirect("application_list")

    return render(request, "applications/apply_application.html", {"job": job})


@login_required
def accept_application(request, app_id):
    application = get_object_or_404(Application, id=app_id)
    userrole = getattr(request.user, "userrole", None)

    # 1. Role check
    if not userrole or userrole.role != "recruiter":
        messages.error(request, "Only recruiters can update applications.")
        return redirect("job_list")

    # 2. Ownership check
    if application.job.user != request.user:
        messages.warning(request, "You can only update applications for your own jobs.")
        return redirect("job_list")

    # 3. Method check
    if request.method != "POST":
        log_activity(
            user=request.user,
            action_type="application_accepted",
            message=f"Accepted application for '{application.job.title}'",
            job=application.job,
            application=application,
        )
        return redirect("view_applicants", slug=application.job.slug)

    # 4. Action
    application.status = "accepted"
    application.save(update_fields=["status"])

    messages.success(request, "Application accepted.")

    # 5. Redirect back
    return redirect("view_applicants", slug=application.job.slug)


@login_required
def reject_application(request, app_id):
    application = get_object_or_404(Application, id=app_id)

    # 1. Role check
    if request.user.userrole.role != "recruiter":
        messages.error(request, "Only recruiters can update applications.")
        return redirect("job_list")

    # 2. Ownership check
    if application.job.user != request.user:
        messages.warning(request, "You can only update applications for your own jobs.")
        return redirect("job_list")

    # 3. Method check
    if request.method != "POST":
        log_activity(
            user=request.user,
            action_type="application_rejected",
            message=f"Rejected application for '{application.job.title}'",
            job=application.job,
            application=application,
        )
        return redirect("view_applicants", slug=application.job.slug)

    # 4. Action
    application.status = "rejected"
    application.save(update_fields=["status"])

    messages.success(request, "Application rejected.")

    # 5. Redirect back
    return redirect("view_applicants", slug=application.job.slug)
