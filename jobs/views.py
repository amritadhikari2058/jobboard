from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, SavedJob, Category
from applications.models import Application
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import JobForm
from .services import JobService
from users.decorators import (
    recruiter_required,
)
from .decorators import job_owner_required
from django.http import JsonResponse


def job_list(request):
    search_query = request.GET.get("q")
    location = request.GET.get("location")
    sort = request.GET.get("sort")
    category = request.GET.get("category")
    user = request.user

    jobs = JobService.get_filtered_jobs(search_query, location, category, sort, user)

    paginator = Paginator(jobs, 10)
    page_number = request.GET.get("page")
    jobs = paginator.get_page(page_number)

    categories = Category.objects.all()

    user_data = JobService.get_jobs_stats(request.user)

    return render(
        request,
        "jobs/job_list.html",
        {
            "jobs": jobs,
            "applied_job_ids": user_data["applied_job_ids"],
            "saved_job_ids": user_data["saved_job_ids"],
            "categories": categories,
        },
    )


def recruiter_jobs(request):
    jobs = Job.objects.filter(user=request.user)
    return render(request, "jobs/recruiter_jobs.html", {"jobs": jobs})


def job_detail(request, id):
    applied_jobs = []
    job = Job.objects.get(id=id)
    application = Application.objects.filter(user=request.user, job=job).first()
    if request.user.is_authenticated:
        applications = Application.objects.filter(user=request.user)
        applied_jobs = [app.job.id for app in applications]
    return render(
        request,
        "jobs/job_detail.html",
        {"job": job, "applied_jobs": applied_jobs, "application": application},
    )


@login_required
@recruiter_required
def create_job(request):

    if request.method == "POST":
        form = JobForm(request.POST)

        if form.is_valid():
            JobService.create_job_service(form, request.user)
            messages.success(request, "Job has successfully created.")
            return redirect("job_list")
    else:
        form = JobForm()
    return render(request, "jobs/create_job.html", {"form": form})


@login_required
@job_owner_required
def update_job(request, id, job):
    job = Job.objects.get(id=id)

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            JobService.update_job_service(form, request.user)
            return redirect("job_list")
    else:
        form = JobForm(instance=job)
    return render(request, "jobs/update_job.html", {"form": form})


@login_required
@job_owner_required
def delete_job(request, id):
    job = Job.objects.get(id=id)

    if request.method == "POST":
        JobService.delete_job_service(request.user, job)
        messages.success(request, "Job deleted successfully")
        return redirect("job_list")

    return render(request, "jobs/delete_job.html", {"job": job})


@login_required
def toggle_save_job(request, job_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid Request"}, status=400)

    job = get_object_or_404(Job, id=job_id)
    added = JobService.toggle_save_job(request.user, job)
    if added:
        messages.success(request, "Job saved.")
    else:
        messages.info(request, "Job removed from saved.")

    return JsonResponse({"added": added})


# Handling saved jobs with separate page
@login_required
def saved_jobs_view(request):
    saved_jobs = (
        SavedJob.objects.filter(user=request.user)
        .select_related("job")
        .order_by("-created_at")
    )
    return render(request, "jobs/saved_jobs.html", {"saved_jobs": saved_jobs})
