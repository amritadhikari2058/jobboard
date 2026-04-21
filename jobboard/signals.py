from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Notification
from applications.models import Application
from .models import UserRole


@receiver(post_save, sender=User)
def userrolesignal(sender, instance, created, **kwargs):
    if created:
        role = "normal_user"
        UserRole.objects.create(user=instance, role=role)


@receiver(pre_save, sender=Application)
def old_status(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Application.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            if instance.status in ["accepted", "rejected"]:
                if instance.status == "accepted":
                    message = (
                        f'Your application for "{instance.job.title}" was accepted'
                    )
                    notif_type = "application_accepted"
                else:
                    message = (
                        f'Your application for "{instance.job.title}" was rejected'
                    )
                    notif_type = "application_rejected"
                Notification.objects.create(
                    user=instance.user,
                    job=instance.job,
                    application=instance,
                    message=message,
                    type=notif_type
                )


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
