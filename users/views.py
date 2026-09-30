from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm, RegisterForm, LoginForm
from applications.models import Application
from django.contrib import messages
from jobs.models import Job
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login, logout, get_user_model
from .decorators import recruiter_required, normal_user_required
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialApp

User = get_user_model()


def configured_social_providers():
    """Provider ids that actually have a SocialApp configured.

    ``{% provider_login_url %}`` raises ``SocialApp.DoesNotExist`` for a
    provider that has no row, which would turn the login and register pages
    into 500s. The social buttons are only rendered for configured providers.
    """
    return list(
        SocialApp.objects.filter(provider__isnull=False)
        .values_list("provider", flat=True)
        .distinct()
    )


# Recruiter Dashboard
@login_required
@recruiter_required
def recruiter_dashboard(request):
    jobs = list(
        Job.objects.filter(recruiter=request.user)
        .prefetch_related("categories")
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

    for job in jobs:
        job.acceptance_rate = (
            round((job.accepted_count / job.total_applications) * 100, 1)
            if job.total_applications
            else 0
        )

    # Totals come from the rows already fetched, so the whole page is one query
    # for jobs plus one per prefetched relation.
    totals = {
        "total_applications": sum(job.total_applications for job in jobs),
        "accepted_applications": sum(job.accepted_count for job in jobs),
        "rejected_applications": sum(job.rejected_count for job in jobs),
        "pending_applications": sum(job.pending_count for job in jobs),
    }

    top_job = max(jobs, key=lambda job: job.total_applications, default=None)

    popular_jobs = sorted(
        (job for job in jobs if job.total_applications),
        key=lambda job: job.total_applications,
        reverse=True,
    )[:5]

    return render(
        request,
        "users/recruiter_dashboard.html",
        {
            "jobs": jobs,
            "total_jobs": len(jobs),
            "total_applications": totals["total_applications"],
            "accepted_applications": totals["accepted_applications"],
            "rejected_applications": totals["rejected_applications"],
            "pending_applications": totals["pending_applications"],
            "top_job": top_job,
            "popular_jobs": popular_jobs,
            "max_applications": popular_jobs[0].total_applications if popular_jobs else 0,
        },
    )


@login_required
@normal_user_required
def user_dashboard(request):
    applications = Application.objects.filter(applicant=request.user).select_related(
        "job__recruiter"
    )

    counts = applications.aggregate(
        total=Count("id"),
        pending=Count("id", filter=Q(status="pending")),
        accepted=Count("id", filter=Q(status="accepted")),
        rejected=Count("id", filter=Q(status="rejected")),
    )

    return render(
        request,
        "users/user_dashboard.html",
        {
            "applications": applications,
            "counts": counts,
        },
    )


@login_required
def edit_user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("users:view_user_profile", profile.user.email)
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "users/profile_edit.html", {"form": form})


@login_required
def view_user_profile(request, email):
    target_user = get_object_or_404(User, email=email)
    profile, created = UserProfile.objects.get_or_create(user=target_user)

    # SELF VIEW
    if request.user == target_user:
        return render(request, "users/profile_detail.html", {"profile": profile})

    # RECRUITER VIEW
    if request.user.role == "recruiter":
        if Application.objects.filter(
            applicant=target_user, job__recruiter=request.user
        ).exists():
            return render(request, "users/profile_detail.html", {"profile": profile})
        return redirect("jobs:job_list")

    messages.warning(request, "You are not eligible to view this user's profile.")
    return redirect("jobs:job_list")


def register_view(request):
    form = RegisterForm()

    if request.method == "POST":
        form = RegisterForm(request.POST)
        role = request.POST.get("role")

        if role not in ["normal_user", "recruiter"]:
            messages.error(request, "Please select a valid role.")
            return render(
                request,
                "users/register.html",
                {"form": form, "social_providers": configured_social_providers()},
            )

        if form.is_valid():
            user = form.save(role=role)

            EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=False,
            )

            messages.success(
                request,
                "Account created! Please check your email to verify your account.",
            )

            return redirect("users:login")

    return render(
        request,
        "users/register.html",
        {"form": form, "social_providers": configured_social_providers()},
    )


def google_register(request):
    role = request.GET.get("role")

    if role not in ["normal_user", "recruiter"]:
        messages.error(request, "Please select a role first.")
        return redirect("users:register")

    request.session["google_registration_role"] = role

    return redirect("google_login")


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=email, password=password)

            if user:
                email_address = EmailAddress.objects.filter(
                    user=user,
                    email=user.email,
                    primary=True,
                ).first()

                if email_address and not email_address.verified:
                    messages.error(
                        request,
                        "Please verify your email address before loggin in.",
                    )

                    return redirect("users:login")

                login(request, user)
                return redirect("jobs:job_list")
            else:
                messages.error(request, "Invalid email or password")

    else:
        form = LoginForm()

    return render(
        request,
        "users/login.html",
        {"form": form, "social_providers": configured_social_providers()},
    )


def logout_view(request):
    logout(request)
    return redirect("users:login")
