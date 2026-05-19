from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm, RegisterForm, LoginForm
from applications.models import Application
from django.contrib import messages
from jobs.models import Job
from django.db import reset_queries
from django.db.models import Count, Q, Sum
from django.contrib.auth import authenticate, login, logout, get_user_model
from .decorators import recruiter_required, normal_user_required

User = get_user_model()


# Recruiter Dashboard
@login_required
@recruiter_required
def recruiter_dashboard(request):
    jobs = (
        Job.objects.filter(user=request.user)
        .select_related("user")
        .annotate(
            total_applications=Count("applications"),
            accepted_count=Count(
                "applications", filter=Q(applications__status="accepted")
            ),
            pending_count=Count(
                "applications", filter=Q(applications__status="pending")
            ),
            rejected_count=Count(
                "applications", filter=Q(applications__status="rejected")
            ),
        )
    )

    total_jobs = jobs.count()
    totals = jobs.aggregate(
        total_applications=Sum("total_applications"),
        accepted_applications=Sum("accepted_count"),
        pending_applications=Sum("pending_count"),
        rejected_applications=Sum("rejected_count"),
    )

    job_titles = [job.title for job in jobs]
    application_counts = [job.total_applications for job in jobs]
    top_job = jobs.order_by("-total_applications").first()

    for job in jobs:
        if job.total_applications > 0:
            job.acceptance_rate = round(
                (job.accepted_count / job.total_applications) * 100, 1
            )
        else:
            job.acceptance_rate = 0

    if top_job and top_job.total_applications > 0:
        top_job.acceptance_rate = round(
            (top_job.accepted_count / top_job.total_applications) * 100, 1
        )
    else:
        top_job.acceptance_rate = 0

    return render(
        request,
        "users/recruiter_dashboard.html",
        {
            "jobs": jobs,
            "total_jobs": total_jobs,
            "total_applications": totals["total_applications"] or 0,
            "accepted_applications": totals["accepted_applications"] or 0,
            "rejected_applications": totals["rejected_applications"] or 0,
            "pending_applications": totals["pending_applications"] or 0,
            "job_titles": job_titles,
            "application_counts": application_counts,
            "top_job": top_job,
        },
    )


@login_required
@normal_user_required
def user_dashboard(request):
    reset_queries()
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
            return redirect("view_user_profile", profile.user.email)
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "users/profile_edit.html", {"form": form})


@login_required
def view_user_profile(request, email):
    target_user = get_object_or_404(User, email=email)
    profile = UserProfile.objects.get_or_create(user=target_user)

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


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully")
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)

            if user:
                login(request, user)
                return redirect("job_list")
            else:
                messages.error(request, "Invalid email or password")

    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")
