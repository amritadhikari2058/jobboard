from applications.models import Application


def get_user_applications(user):
    return (
        Application.objects.filter(user=user)
        .select_related("job", "user")
        .order_by("-id")
    )


def get_job_applications(job):
    return (
        Application.objects.filter(job=job)
        .select_related("job", "user")
        .order_by("=id")
    )


def get_application_by_id(app_id):
    return Application.objects.filter(id=app_id).select_related("job", "user").first()
