from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Application
from jobboard.models import Job
from django.contrib.auth.decorators import login_required
from .services import ApplicationService
from users.decorators import normal_user_required, recruiter_required, job_owner_required, recruiter_owns_application

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
        resume = request.FILES.get("resume")
        status = request.POST.get("status")
        application = ApplicationService.update_application(application, resume)

        messages.success(request, 'Application updated successfully')
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

    if request.method == "POST":
        resume = request.FILES.get("resume")

        success, result = ApplicationService.apply(
            user=request.user, job=job, resume=resume
        )

        if not success:
            messages.warning(request, result)
            return redirect("application_list")

        messages.success(request, "Application applied successfully!")
        return redirect("application_list")

    return render(request, "applications/apply_application.html", {"job": job})


@login_required
def accept_application(request, app_id):
    application = get_object_or_404(Application, id=app_id)

    # 3. Method check
    if request.method != "POST":
        return redirect("view_applicants", slug=application.job.slug)

    success, result = ApplicationService.update_application_status(
        application, request.user, "accepted"
    )

    if not success:
        messages.error(request, result)

    messages.success(request, "Application accepted.")
    return redirect("view_applicants", slug=application.job.slug)


@login_required
def reject_application(request, app_id):
    application = get_object_or_404(Application, id=app_id)

    # 3. Method check
    if request.method != "POST":
        return redirect("view_applicants", slug=application.job.slug)

    success, result = ApplicationService.update_application_status(
        application, request.user, "rejected"
    )

    if not success:
        messages.error(request, result)
        return redirect("job_list")

    messages.success(request, "Application rejected.")
    return redirect("view_applicants", slug=application.job.slug)


@login_required
def view_applicants(request, slug):
    user = request.user

    if user.userrole.role != "recruiter":
        messages.info(request, "Only recruiters have access to the applicant's list")
        return redirect("job_list")

    job = get_object_or_404(Job, slug=slug, user=user)
    applications = Application.objects.filter(job=job)

    return render(
        request, "jobboard/view_applicants.html", {"applications": applications}
    )
