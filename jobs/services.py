from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Q

from .models import Job, SavedJob
from applications.models import Application
from notifications.utils import log_activity


POPULAR_JOBS_CACHE_KEY = "jobs:popular"


class JobService:
    @staticmethod
    def get_filtered_jobs(query, location, category, sort, user):
        jobs = Job.objects.all()

        # Recruiter sees only their jobs
        if user.is_authenticated and user.role == "recruiter":
            jobs = jobs.filter(recruiter=user)

        jobs = jobs.annotate(
            total_applications=Count("applications"),
            accepted_count=Count(
                "applications", filter=Q(applications__status="accepted")
            ),
            pending_count=Count(
                "applications", filter=Q(applications__status="pending")
            ),
        )

        if query:
            jobs = jobs.filter(title__icontains=query)

        if location:
            jobs = jobs.filter(location__icontains=location)

        if category:
            jobs = jobs.filter(categories__name__icontains=category)

        jobs = jobs.distinct()
        jobs = jobs.order_by("-created_at")

        if sort == "latest":
            jobs = jobs.order_by("-created_at")
        elif sort == "oldest":
            jobs = jobs.order_by("created_at")

        return jobs

    @staticmethod
    def get_popular_jobs(limit=None):
        """Return the most applied-to jobs, breaking ties on saves then age.

        Only the ordered list of ids is cached, because the ranking aggregation
        is the expensive part and re-reading those rows by id costs one cheap
        query. jobs.signals drops the entry whenever a job, an application or a
        saved job changes. Passing a `limit` other than the configured default
        skips the cache, since only one window is kept.
        """
        limit = limit or settings.POPULAR_JOBS_LIMIT
        cacheable = limit == settings.POPULAR_JOBS_LIMIT

        job_ids = cache.get(POPULAR_JOBS_CACHE_KEY) if cacheable else None

        if job_ids is None:
            job_ids = list(
                Job.objects.annotate(
                    total_applications=Count("applications", distinct=True),
                    total_saves=Count("savedjob", distinct=True),
                )
                .order_by("-total_applications", "-total_saves", "-created_at")
                .values_list("id", flat=True)[:limit]
            )

            if cacheable:
                cache.set(
                    POPULAR_JOBS_CACHE_KEY,
                    job_ids,
                    settings.POPULAR_JOBS_CACHE_TTL,
                )

        jobs_by_id = Job.objects.in_bulk(job_ids)
        return [jobs_by_id[job_id] for job_id in job_ids if job_id in jobs_by_id]

    @staticmethod
    def get_jobs_stats(user):
        if not user.is_authenticated:
            return {
                "applied_job_ids": [],
                "saved_job_ids": [],
                "counts": {},
            }

        applications = Application.objects.filter(applicant=user)

        return {
            "applied_job_ids": [app.job.id for app in applications],
            "saved_job_ids": SavedJob.objects.filter(applicant=user)
            .select_related("job")
            .values_list("job_id", flat=True),
            "counts": {
                "total": applications.count(),
                "pending": applications.filter(status="pending").count(),
                "accepted": applications.filter(status="accepted").count(),
                "rejected": applications.filter(status="rejected").count(),
            },
        }

    @staticmethod
    def toggle_save_job(user, job):
        saved_job = SavedJob.objects.filter(applicant=user, job=job).first()

        if saved_job:
            saved_job.delete()
            return False
        else:
            SavedJob.objects.create(applicant=user, job=job)
            return True

    @staticmethod
    def create_job_service(form, user):
        job = form.save(commit=False)
        job.recruiter = user
        job.save()
        form.save_m2m()

        log_activity(
            user=user,
            action_type="job_created",
            message=f"Created job '{job.title}'",
            job=job,
        )

        return job

    @staticmethod
    def update_job_service(form, user):
        job = form.save()
        log_activity(
            user=user,
            action_type="job_updated",
            message=f"Updated job '{job.title}'",
            job=job,
        )
        return job

    @staticmethod
    def delete_job_service(user, job):
        log_activity(
            user=user,
            action_type="job_deleted",
            message=f"Deleted job '{job.title}'",
            job=job,
        )
        job.delete()
