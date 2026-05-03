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

    @staticmethod
    def update_application_status(application, user, status):
        # 1. Role Check
        userrole = getattr(user, 'userrole', None)
        if not userrole or userrole.role != 'recruiter':
            return False, 'Only recruiters can update applications.'
        
        # 2. Ownership Check
        if application.job.user != user:
            return False, 'You can only update applications for your own jobs.'
        
        # 3. Update Status
        application.status = status
        application.save(update_Fields = ['status'])

        # 4. Log activity
        action = 'application_accepted' if status == 'accepted' else 'applicaton_rejected'

        activity_logs(
            user=user,
            action_type=action,
            message=f"{status.capitalizer()} application for '{application.job.title}'",
            job=application.job,
            application=application,
        )

        return True, application
    
    @staticmethod
    def update_application(application, resume, status):
        if resume:
            application.resume = resume
        application.save(update_fields = ['resume'])

        return application