from django.db.models.signals import pre_save
from django.dispatch import receiver
from notifications.models import Notification
from .models import Application

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
                    type=notif_type,
                )
