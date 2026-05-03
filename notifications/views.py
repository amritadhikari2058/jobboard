from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification, ActivityLog
from django.core.paginator import Paginator
from django.db.models import Q
from .services import get_activity_logs_for_user

# Notifications View
@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )
    return render(
        request, "notifications/notifications.html", {"notifications": notifications}
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
    logs = get_activity_logs_for_user(request.user)
    
    paginator = Paginator(logs, 10)
    page = request.GET.get("page")
    logs = paginator.get_page(page)

    return render(request, "notifications/activity_logs.html", {"logs": logs})
