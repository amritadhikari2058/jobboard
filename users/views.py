from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm
from django.contrib.auth.models import User
from applications.models import Application
from django.contrib import messages
from jobboard.models import Job
from django.db import reset_queries


# Recruiter Dashboard
@login_required
def recruiter_dashboard(request):
    if request.user.userrole.role != "recruiter":
        return redirect("job_list")
    jobs = Job.objects.filter(user=request.user).prefetch_related("applications")
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


@login_required
def edit_user_profile(request):
    print("METHOD:", request.method)
    print("Edit View Hit")
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("view_user_profile", profile.user.username)
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "jobboard/profile_edit.html", {"form": form})


@login_required
def view_user_profile(request, username):
    print("METHOD:", request.method)
    print("View View Hit")
    target_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=target_user)

    # SELF VIEW
    if request.user == target_user:
        return render(request, "jobboard/profile_detail.html", {"profile": profile})

    # RECRUITER VIEW
    if request.user.userrole.role == "recruiter":
        if Application.objects.filter(
            user=target_user, job__user=request.user
        ).exists():
            return render(request, "jobboard/profile_detail.html", {"profile": profile})
        return redirect("job_list")

    messages.warning(request, "You are not eligible to view this user's profile.")
    return redirect("job_list")
