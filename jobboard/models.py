from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=False)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.TextField(null=False)
    location = models.CharField(max_length=100, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]


class UserRole(models.Model):
    CHOICES = [("normal_user", "Normal User"), ("recruiter", "Recruiter")]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userrole')
    role = models.CharField(choices=CHOICES, default="normal_user", max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}'s role"
