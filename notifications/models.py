from django.db import models
from django.contrib.auth.models import User
from jobboard.models import Job


class Notification(models.Model):
    STATUS_CHOICES = [
        ("application_created", "Application Created"),
        ("application_accepted", "Application Accepted"),
        ("application_rejected", "Application Rejected"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    application = models.ForeignKey(
        "applications.Application", on_delete=models.CASCADE, null=True, blank=True
    )
    message = models.TextField()
    type = models.CharField(
        choices=STATUS_CHOICES, default="application_created", max_length=30
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.message}"


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("job_created", "Job Created"),
        ("job_updated", "Job Updated"),
        ("job_deleted", "Job Deleted"),
        ("application_created", "Application Created"),
        ("application_accepted", "Application Accepted"),
        ("application_rejected", "Application Rejected"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=75, choices=ACTION_CHOICES)
    message = models.TextField()

    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    application = models.ForeignKey(
        "applications.Application", on_delete=models.CASCADE, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action_type}"
