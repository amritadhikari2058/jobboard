from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=False)
    slug = models.SlugField(unique=True, null=True, blank=True)
    location = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)
    categories = models.ManyToManyField(Category, blank=True)
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userrole")
    role = models.CharField(choices=CHOICES, default="normal_user", max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}'s role"


class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "job")

    def __str__(self):
        return f"{self.user} saved job {self.job}"


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


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return self.user.username


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('job_created', 'Job Created'),
        ('job_updated', 'Job Updated'),
        ('job_deleted', 'Job Deleted'),
        ('application_created', 'Application Created'),
        ('application_accepted', 'Application Accepted'),
        ('application_rejected', 'Application Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=75, choices=ACTION_CHOICES)
    message = models.TextField()

    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    application = models.ForeignKey('applications.Application', on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action_type}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    skills = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=50, blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name_plural = 'User Profiles'