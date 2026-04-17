from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserRole


@receiver(post_save, sender=User)
def userrolesignal(sender, instance, created, **kwargs):
    if created:
        role = "normal_user"
        UserRole.objects.create(user=instance, role=role)
