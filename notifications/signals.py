from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from applications.models import Application


@receiver(post_save, sender=Application)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.job.user,
            job=instance.job,
            application=instance,
            message=f'New Application received for "{instance.job.title}"',
            type="application_created",
        )
