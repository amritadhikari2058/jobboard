from unittest import mock

from django.core.cache import cache, caches
from django.test import TestCase, override_settings

from applications.models import Application
from users.models import User

from .models import Job, SavedJob
from .services import POPULAR_JOBS_CACHE_KEY, JobService


TEST_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "jobboard-tests",
    }
}


@override_settings(CACHES=TEST_CACHES)
class PopularJobsTestCase(TestCase):
    """Base fixture helpers. Cache is always LocMem so tests never touch Redis."""

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)

        self.recruiter = User.objects.create_user(
            email="recruiter@example.com", password="pw", role="recruiter"
        )
        self.applicants = [
            User.objects.create_user(email=f"a{i}@example.com", password="pw")
            for i in range(6)
        ]

    def make_job(self, title, created_at=None):
        job = Job.objects.create(
            recruiter=self.recruiter,
            title=title,
            location="Remote",
            description="desc",
        )
        if created_at is not None:
            # created_at is auto_now_add, so it can only be set via a direct UPDATE.
            Job.objects.filter(pk=job.pk).update(created_at=created_at)
            job.refresh_from_db()
        return job

    def apply(self, job, applicant):
        return Application.objects.create(applicant=applicant, job=job)

    def prime_cache(self):
        JobService.get_popular_jobs()
        self.assertIsNotNone(cache.get(POPULAR_JOBS_CACHE_KEY))


class PopularJobsRankingTests(PopularJobsTestCase):
    def test_returns_empty_when_there_are_no_jobs(self):
        self.assertEqual(JobService.get_popular_jobs(), [])

    def test_ranks_by_application_count(self):
        low = self.make_job("Low")
        high = self.make_job("High")
        mid = self.make_job("Mid")

        self.apply(mid, self.applicants[0])
        self.apply(high, self.applicants[0])
        self.apply(high, self.applicants[1])

        result = JobService.get_popular_jobs()

        self.assertEqual([job.pk for job in result], [high.pk, mid.pk, low.pk])

    def test_counts_are_not_inflated_by_the_join(self):
        # A job with 2 applications and 3 saves fans out to 6 rows. Without
        # distinct=True both jobs would tie on an inflated count of 6.
        both = self.make_job("Both")
        apps_only = self.make_job("AppsOnly")

        for applicant in self.applicants[:2]:
            self.apply(both, applicant)
            self.apply(apps_only, applicant)
        for applicant in self.applicants[:3]:
            SavedJob.objects.create(applicant=applicant, job=both)

        result = JobService.get_popular_jobs()

        self.assertEqual([job.pk for job in result], [both.pk, apps_only.pk])

    def test_saves_break_application_ties(self):
        unsaved = self.make_job("Unsaved")
        saved = self.make_job("Saved")

        for applicant in self.applicants[:2]:
            self.apply(unsaved, applicant)
            self.apply(saved, applicant)
        SavedJob.objects.create(applicant=self.applicants[0], job=saved)

        result = JobService.get_popular_jobs()

        self.assertEqual([job.pk for job in result], [saved.pk, unsaved.pk])

    def test_newest_breaks_remaining_ties(self):
        from datetime import timedelta
        from django.utils import timezone

        now = timezone.now()
        old = self.make_job("Old", created_at=now - timedelta(days=2))
        new = self.make_job("New", created_at=now)

        result = JobService.get_popular_jobs()

        self.assertEqual([job.pk for job in result], [new.pk, old.pk])

    def test_respects_limit(self):
        for i in range(3):
            self.make_job(f"Job {i}")

        self.assertEqual(len(JobService.get_popular_jobs(limit=2)), 2)

    def test_drops_cached_ids_for_jobs_deleted_while_cached(self):
        job = self.make_job("Only Job")
        self.assertEqual([j.pk for j in JobService.get_popular_jobs()], [job.pk])

        job.delete()

        self.assertEqual(JobService.get_popular_jobs(), [])


class PopularJobsCachingTests(PopularJobsTestCase):
    def test_cache_miss_ranks_then_caches(self):
        self.make_job("Only Job")

        with self.assertNumQueries(2):
            JobService.get_popular_jobs()

        self.assertIsNotNone(cache.get(POPULAR_JOBS_CACHE_KEY))

    def test_cache_hit_skips_the_aggregation(self):
        self.make_job("Only Job")
        JobService.get_popular_jobs()

        with self.assertNumQueries(1):
            JobService.get_popular_jobs()

    def test_custom_limit_bypasses_the_cache(self):
        self.make_job("Only Job")

        JobService.get_popular_jobs(limit=1)

        self.assertIsNone(cache.get(POPULAR_JOBS_CACHE_KEY))

    @override_settings(POPULAR_JOBS_CACHE_TTL=60)
    def test_uses_configured_ttl(self):
        self.make_job("Only Job")

        with mock.patch.object(type(caches["default"]), "set") as cache_set:
            JobService.get_popular_jobs()

        cache_set.assert_called_once()
        self.assertEqual(cache_set.call_args.args[2], 60)


class PopularJobsInvalidationTests(PopularJobsTestCase):
    def assertCacheCleared(self):
        self.assertIsNone(cache.get(POPULAR_JOBS_CACHE_KEY))

    def test_creating_a_job_invalidates(self):
        self.prime_cache()

        self.make_job("Brand New")

        self.assertCacheCleared()

    def test_updating_a_job_invalidates(self):
        job = self.make_job("Original")
        self.prime_cache()

        job.title = "Renamed"
        job.save()

        self.assertCacheCleared()

    def test_deleting_a_job_invalidates(self):
        job = self.make_job("Doomed")
        self.prime_cache()

        job.delete()

        self.assertCacheCleared()

    def test_creating_an_application_invalidates(self):
        job = self.make_job("Popular")
        self.prime_cache()

        self.apply(job, self.applicants[0])

        self.assertCacheCleared()

    def test_changing_application_status_invalidates(self):
        job = self.make_job("Popular")
        application = self.apply(job, self.applicants[0])
        self.prime_cache()

        application.status = "accepted"
        application.save()

        self.assertCacheCleared()

    def test_deleting_an_application_invalidates(self):
        job = self.make_job("Popular")
        application = self.apply(job, self.applicants[0])
        self.prime_cache()

        application.delete()

        self.assertCacheCleared()

    def test_saving_a_job_invalidates(self):
        job = self.make_job("Popular")
        self.prime_cache()

        JobService.toggle_save_job(self.applicants[0], job)

        self.assertCacheCleared()

    def test_unsaving_a_job_invalidates(self):
        job = self.make_job("Popular")
        JobService.toggle_save_job(self.applicants[0], job)
        self.prime_cache()

        JobService.toggle_save_job(self.applicants[0], job)

        self.assertCacheCleared()

    def test_new_rankings_are_visible_after_invalidation(self):
        stale = self.make_job("Stale")
        self.prime_cache()

        fresh = self.make_job("Fresh")
        for applicant in self.applicants[:2]:
            self.apply(fresh, applicant)

        result = JobService.get_popular_jobs()

        self.assertEqual([job.pk for job in result], [fresh.pk, stale.pk])
