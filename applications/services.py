from .models import Application
from notifications.views import activity_logs


class ApplicationService:
    @staticmethod
    def apply(user, job, resume):

        # Check if already applied
        if Application.objects.filter(user=user, job=job).exists():
            return False, "You have already applied for this job."

        # Create Application
        application = Application.objects.create(user=user, job=job, resume=resume)

        # log_activity
        activity_logs(
            user=user,
            action_type="application_created",
            message=f"Applied to '{job.title}'",
            job=job,
            application=application,
        )

        return True, application
