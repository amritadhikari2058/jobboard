from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, User, SavedJob
from applications.models import Application
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def job_list(request):
    jobs = Job.objects.all()
    applied_jobs = []
    saved_jobs = []
    total_application_count = 0
    pending_application_count = 0
    accepted_application_count = 0
    rejected_application_count = 0

    if request.user.is_authenticated:
        applications = Application.objects.filter(user=request.user)
        total_application_count = applications.count()
        pending_application_count = applications.filter(status="pending").count()
        accepted_application_count = applications.filter(status="accepted").count()
        rejected_application_count = applications.filter(status="rejected").count()
        applied_jobs = [app.job.id for app in applications]
        saved = SavedJob.objects.filter(user=request.user)
        saved_jobs = [s.job.id for s in saved]
    return render(
        request,
        "jobboard/job_list.html",
        {
            "jobs": jobs,
            "applied_jobs": applied_jobs,
            "total_application_count": total_application_count,
            "accepted_application_count": accepted_application_count,
            "rejected_application_count": rejected_application_count,
            "pending_application_count": pending_application_count,
            'saved_jobs': saved_jobs
        },
    )


def job_detail(request, id):
    job = Job.objects.get(id=id)
    return render(request, "jobboard/job_detail.html", {"job": job})


@login_required
def create_job(request):
    userrole = request.user.userrole
    if userrole.role != "recruiter":
        messages.error(request, "Only recruiters can create a job.")
        return redirect("job_list")
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        location = request.POST.get("location")
        print(request.user)
        job = Job(
            title=title, description=description, location=location, user=request.user
        )
        job.save()
        messages.success(request, "Job has successfully created.")
        return redirect("job_list")
    return render(request, "jobboard/create_job.html")


@login_required
def update_job(request, id):
    job = Job.objects.get(id=id)
    if request.method == "POST":
        job.title = request.POST.get("title")
        job.description = request.POST.get("description")
        job.location = request.POST.get("location")

        job.save()

        return redirect("job_list")

    return render(request, "jobboard/update_job.html", {"job": job})


@login_required
def delete_job(request, id):
    job = Job.objects.get(id=id)
    if request.method == "POST":
        job.delete()
        return redirect("job_list")

    return render(request, "jobboard/delete_job.html")


@login_required
def recruiter_dashboard(request):
    user = request.user
    if user.userrole.role != "recruiter":
        messages.info(request, "Only recruiters have the recruiters dashboard.")
        return redirect("job_list")
    jobs = Job.objects.filter(user=user)
    return render(request, "jobboard/recruiter_dashboard.html", {"jobs": jobs})


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

@login_required
def toggle_save_job(request, job_id):
    print("TOGGLE VIEW HIT")
    print(request.method)
    if request.method != 'POST':
        return redirect('job_list')
    userrole = getattr(request.user, 'userrole', None)
    if not userrole or userrole.role != 'normal_user':
        messages.error(request, 'Only normal users can save jobs.')
        return redirect('job_list')
    job = get_object_or_404(Job, id=job_id)
    saved_job = SavedJob.objects.filter(user=request.user, job=job).first()
    if saved_job:
        saved_job.delete()
    else:
        SavedJob.objects.create(user=request.user, job=job)
    return redirect('job_list')