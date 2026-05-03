from django.db.models import Q
from .models import ActivityLog

def get_activity_logs_for_user(user):
    role = user.userrole.role

    if role == "normal_user":
        logs = ActivityLog.objects.filter(Q(user=user) | Q(application__user=user))
    
    elif role == "recruiter":
        logs = ActivityLog.objects.filter(Q(user=user) | Q(job__user=user))
    
    else:
        return ActivityLog.objects.none()
    
    return logs.select_related('job', 'application', 'user').order_by('-created_at')