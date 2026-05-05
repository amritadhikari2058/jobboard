from .models import Application
from notifications.utils import log_activity
from .exceptions import DuplicateApplicationError, InvalidApplicationStateError
from notifications.services import NotificationService


class ApplicationService:
    @staticmethod
    def apply(user, job, resume):
        existing = Application.objects.filter(user=user, job=job).first()

        if existing:
            raise DuplicateApplicationError("You have already applied for this job")

        # Create Application
        application = Application.objects.create(user=user, job=job, resume=resume)

        # log_activity
        log_activity(
            user=user,
            action_type="application_created",
            message=f"Applied to '{job.title}'",
            job=job,
            application=application,
        )

        return application

    @staticmethod
    def update_application_status(application, user, status):
        if application.status == status:
            raise InvalidApplicationStateError(f"Application is already {status}")

        application.status = status
        application.save(update_fields=["status"])

        NotificationService.notify(
            user=application.user,
            message=f"Your application for '{application.job.title}' was {status}",
        )

        log_activity(
            user=user,
            action_type=f"application_{status}",
            message=f"{status.capitalizer()} application for '{application.job.title}'",
            job=application.job,
            application=application,
        )

        return True, application

    @staticmethod
    def update_application(application, resume, status):
        if resume:
            application.resume = resume
            application.save(update_fields=["resume"])

        return application

    @staticmethod
    def delete_application(application, user):
        job = application.job
        application.delete()

        NotificationService.notify(
            user=application.job.user,
            message=f"{user.username} withdrew application from '{application.job.title}'",
        )

        log_activity(
            user=user,
            action_type="application_deleted",
            message=f"Deleted application for '{job.title}'",
            job=job,
        )
