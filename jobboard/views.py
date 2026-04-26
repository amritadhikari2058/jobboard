from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, SavedJob, Notification, Category
from applications.models import Application
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import JobForm
from django.db import connection, reset_queries
from .utils import log_activity


def job_list(request):
    search_query = request.GET.get("q")
    location = request.GET.get("location")
    sort = request.GET.get("sort")
    category = request.GET.get("category")
    jobs = Job.objects.all()
    if search_query:
        jobs = jobs.filter(title__icontains=search_query)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if category:
        jobs = jobs.filter(categories__name__icontains=category)
    jobs = jobs.distinct()
    if sort == "latest":
        jobs = jobs.order_by("-created_at")
    elif sort == "oldest":
        jobs = jobs.order_by("created_at")
    paginator = Paginator(jobs, 4)
    page_number = request.GET.get("page")
    jobs = paginator.get_page(page_number)
    categories = Category.objects.all()

    applied_jobs = []
    saved_jobs = []
    total_application_count = 0
    pending_application_count = 0
    accepted_application_count = 0
    rejected_application_count = 0
    saved_job_ids = []

    if request.user.is_authenticated:
        applications = Application.objects.filter(user=request.user)
        total_application_count = applications.count()
        pending_application_count = applications.filter(status="pending").count()
        accepted_application_count = applications.filter(status="accepted").count()
        rejected_application_count = applications.filter(status="rejected").count()
        applied_jobs = [app.job.id for app in applications]
        saved_jobs = SavedJob.objects.filter(user=request.user).select_related("job")
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
            "saved_jobs": saved_jobs,
            "categories": categories,
        },
    )


def job_detail(request, id):
    applied_jobs = []
    job = Job.objects.get(id=id)
    application = Application.objects.filter(user=request.user, job=job).first()
    if request.user.is_authenticated:
        applications = Application.objects.filter(user=request.user)
        applied_jobs = [app.job.id for app in applications]
    return render(
        request,
        "jobboard/job_detail.html",
        {"job": job, "applied_jobs": applied_jobs, "application": application},
    )


@login_required
def create_job(request):
    userrole = request.user.userrole
    if userrole.role != "recruiter":
        messages.error(request, "Only recruiters can create a job.")
        return redirect("job_list")
    form = JobForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()
            form.save_m2m()

            log_activity(
                user=request.user,
                action_type="job_created",
                message=f"Created job '{job.title}'",
                job=job,
            )
            messages.success(request, "Job has successfully created.")
            return redirect("job_list")
        else:
            form = JobForm()
    return render(request, "jobboard/create_job.html", {"form": form})


@login_required
def update_job(request, id):
    job = Job.objects.get(id=id)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            log_activity(
                user=request.user,
                action_type="job_updated",
                message=f"Updated job '{job.title}'",
                job=job,
            )
            return redirect("job_list")
    else:
        form = JobForm(instance=job)
    return render(request, "jobboard/update_job.html", {"form": form})


@login_required
def delete_job(request, id):
    job = Job.objects.get(id=id)
    if request.method == "POST":
        log_activity(
            user=request.user,
            action_type="job_deleted",
            message=f"Deleted job '{job.title}'",
        )
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
    if request.method != "POST":
        return redirect("job_list")
    userrole = getattr(request.user, "userrole", None)
    if not userrole or userrole.role != "normal_user":
        messages.error(request, "Only normal users can save jobs.")
        return redirect("job_list")
    job = get_object_or_404(Job, id=job_id)
    saved_job = SavedJob.objects.filter(user=request.user, job=job).first()
    if saved_job:
        saved_job.delete()
    else:
        SavedJob.objects.create(user=request.user, job=job)
    return redirect(request.META.get("HTTP_REFERRER", "job_list"))


# Handling saved jobs with separate page
@login_required
def saved_jobs_view(request):
    saved_jobs = SavedJob.objects.filter(user=request.user).select_related("job")
    return render(request, "jobboard/saved_jobs.html", {"saved_jobs": saved_jobs})


# Notifications View
@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )
    return render(
        request, "jobboard/notifications.html", {"notifications": notifications}
    )


# Mark as read + Redirect View
@login_required
def notifications_mark_as_read(request, id):
    notification = get_object_or_404(Notification, id=id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect("job_detail", id=notification.job.id)


# Recruiter Dashboard
@login_required
def recruiter_dashboard(request):
    if request.user.userrole.role != "recruiter":
        return redirect("job_list")
    jobs = Job.objects.filter(user=request.user).prefetch_related("application_set")
    return render(
        request,
        "jobboard/recruiter_dashboard.html",
        {"jobs": jobs},
    )


@login_required
def user_dashboard(request):
    reset_queries()
    if request.user.userrole.role != "normal_user":
        return redirect("job_list")
    applications = Application.objects.filter(user=request.user).select_related("job")
    response = render(
        request, "jobboard/user_dashboard.html", {"applications": applications}
    )
    return response
