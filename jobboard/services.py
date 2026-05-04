from .models import Job, SavedJob
from applications.models import Application
from notifications.utils import log_activity


def get_filtered_jobs(query, location, category, sort):
    jobs = Job.objects.all()

    if query:
        jobs = jobs.filter(title__icontains=query)

    if location:
        jobs = jobs.filter(location__icontains=location)

    if category:
        jobs = jobs.filter(categories__name__icontains=category)

    jobs = jobs.distinct()

    if sort == "latest":
        jobs = jobs.order_by("-created_at")
    elif sort == "oldest":
        jobs = jobs.order_by("created_at")

    return jobs


def get_user_jobs_data(user):
    if not user.is_authenticated:
        return {
            "applied_jobs": [],
            "saved_jobs": [],
            "counts": {},
        }

    applications = Application.objects.filter(user=user)

    return {
        "applied_jobs": [app.job.id for app in applications],
        "saved_jobs": SavedJob.objects.filter(user=user).select_related("job"),
        "counts": {
            "total": applications.count(),
            "pending": applications.filter(status="pending").count(),
            "accepted": applications.filter(status="accepted").count(),
            "rejected": applications.filter(status="rejected").count(),
        },
    }


def toggle_save_job(user, job):
    saved_job = SavedJob.objects.filter(user=user, job=job).first()

    if saved_job():
        saved_job.delete()
        return False
    else:
        SavedJob.objects.create(user=user, job=job)
        return True


def create_job_service(form, user):
    job = form.save(commit=False)
    job.user = user
    job.save()
    form.save_m2m()

    log_activity(
        user=user,
        action_type="job_created",
        message=f"Created job '{job.title}'",
        job=job,
    )

    return job


def update_job_service(form, user):
    job = form.save()
    log_activity(
        user=user,
        action_type="job_updated",
        message=f"Updated job '{job.title}'",
        job=job,
    )
    return job


def delete_job_service(user, job):
    log_activity(
        user=user,
        action_type="job_deleted",
        message=f"Deleted job '{job.title}'",
        job=job,
    )
    job.delete()
