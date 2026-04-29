from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification, ActivityLog
from django.core.paginator import Paginator
from django.db.models import Q


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


@login_required
def activity_logs(request):
    user = request.user
    role = user.userrole.role

    if role == "normal_user":
        logs = ActivityLog.objects.filter(Q(user=user) | Q(application__user=user))

    elif role == "recruiter":
        logs = ActivityLog.objects.filter(Q(user=user) | Q(job__user=user))

    else:
        logs = ActivityLog.objects.none()

    logs.select_related("job", "application", "user")
    logs = logs.order_by("-created_at")[:20]

    paginator = Paginator(logs, 10)
    page = request.GET.get("page")
    logs = paginator.get_page(page)

    return render(request, "jobboard/activity_logs.html", {"logs": logs})
