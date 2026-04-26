from .models import ActivityLog

def log_activity(user, action_type, message, job=None, application=None):
    ActivityLog.objects.create(
        user=user,
        action_type=action_type,
        message=message,
        job=job,
        application=application
    )