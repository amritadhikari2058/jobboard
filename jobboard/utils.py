from .models import ActivityLog

def log_activity(user, action_type, message, job=None, application=None):
    if action_type == 'job_created':
        message = f"You created job '{job.title}'"
    elif action_type == 'application_created':
        message = f"You applied to '{job.title}'"
    elif action_type == 'application_accepted':
        message = f"Application accepted for '{job.title}'"
    elif action_type == 'application_rejected':
        message = f"Application rejected for '{job.title}'"
    else:
        message = action_type

    ActivityLog.objects.create(
        user=user,
        action_type=action_type,
        message=message,
        job=job,
        application=application
    )