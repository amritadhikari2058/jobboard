from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm
from django.contrib.auth.models import User
from applications.models import Application
from django.contrib import messages
from jobboard.models import Job
from django.db import reset_queries
from django.db.models import Count, Q


# Recruiter Dashboard
@login_required
def recruiter_dashboard(request):
    if request.user.userrole.role != "recruiter":
        return redirect("job_list")

    jobs = Job.objects.filter(user=request.user).annotate(
        total_applications=Count("applications"),
        accepted_count=Count("applications", filter=Q(applications__status="accepted")),
        pending_count=Count("applications", filter=Q(applications__status="pending")),
        rejected_count=Count("applications", filter=Q(applications__status="rejected")),
    )

    total_jobs = jobs.count()
    total_applications = sum(job.total_applications for job in jobs)
    accepted_applications = sum(job.accepted_count for job in jobs)
    pending_applications = sum(job.pending_count for job in jobs)
    rejected_applications = sum(job.rejected_count for job in jobs)

    job_titles = [job.title for job in jobs]
    application_counts = [job.total_applications for job in jobs]
    top_job = jobs.order_by('-total_applications').first()

    for job in jobs:
        if job.total_applications > 0:
            job.acceptance_rate = round(
                (job.accepted_count / job.total_applications) * 100, 1
            )
        else:
            job.acceptance_rate = 0
    
    if top_job and top_job.total_applications > 0:
        top_job.acceptance_rate = round(
            (top_job.accepted_count / top_job.total_applications) *100, 1
        )
    else:
        top_job.acceptance_rate=0

    return render(
        request,
        "users/recruiter_dashboard.html",
        {
            "jobs": jobs,
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "accepted_applications": accepted_applications,
            "rejected_applications": rejected_applications,
            "pending_applications": pending_applications,
            'job_titles': job_titles,
            'application_counts': application_counts,
            'top_job': top_job,
        },
    )


@login_required
def user_dashboard(request):
    reset_queries()
    if request.user.userrole.role != "normal_user":
        return redirect("job_list")
    applications = Application.objects.filter(user=request.user).select_related("job")
    response = render(
        request, "users/user_dashboard.html", {"applications": applications}
    )
    return response


@login_required
def edit_user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("view_user_profile", profile.user.username)
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "users/profile_edit.html", {"form": form})


@login_required
def view_user_profile(request, username):
    target_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=target_user)

    # SELF VIEW
    if request.user == target_user:
        return render(request, "users/profile_detail.html", {"profile": profile})

    # RECRUITER VIEW
    if request.user.userrole.role == "recruiter":
        if Application.objects.filter(
            user=target_user, job__user=request.user
        ).exists():
            return render(request, "users/profile_detail.html", {"profile": profile})
        return redirect("job_list")

    messages.warning(request, "You are not eligible to view this user's profile.")
    return redirect("job_list")
