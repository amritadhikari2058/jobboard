from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from applications.models import Application

from .models import Job, SavedJob
from .services import POPULAR_JOBS_CACHE_KEY


def invalidate_popular_jobs_cache():
    cache.delete(POPULAR_JOBS_CACHE_KEY)


@receiver(post_save, sender=Job)
@receiver(post_delete, sender=Job)
@receiver(post_save, sender=Application)
@receiver(post_delete, sender=Application)
@receiver(post_save, sender=SavedJob)
@receiver(post_delete, sender=SavedJob)
def popular_jobs_cache_invalidation(sender, **kwargs):
    invalidate_popular_jobs_cache()
