from django.db import models
from django.contrib.auth.models import User


class Application(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("withdrawn", "Withdrawn"),
    ]

    AVAILABILITY_TYPE_CHOICES = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("internship", "Internship"),
    ]

    RATING_CHOICES = [
        (1, "1 - Poor"),
        (2, "2 - Fair"),
        (3, "3 - Good"),
        (4, "4 - Very Good"),
        (5, "5 - Excellent"),
    ]

    TAG_CHOICES = [
        ("strong", "Strong Candidate"),
        ("weak", "Weak Candidate"),
        ("review", "Needs Review"),
    ]

    # Core relations
    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    # Applicant data
    resume = models.FileField(upload_to="resumes/", null=True, blank=True)
    cover_letter = models.TextField(
        max_length=1000, default="Put your Cover Letter here"
    )
    experience = models.TextField(max_length=750, default="No Experience")
    skills = models.CharField(max_length=250, blank=True)

    # Availability
    availability_type = models.CharField(
        choices=AVAILABILITY_TYPE_CHOICES,
        max_length=15,
        default="full_time",
    )
    availability_period = models.CharField(
        max_length=50,
        default="Immediate",
        help_text="e.g. Immediate, 2 weeks, 1 month",
    )

    # Salary
    expected_salary = models.PositiveIntegerField(null=True, blank=True)

    # Recruiter-side fields
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)
    tags = models.CharField(
        choices=TAG_CHOICES,
        max_length=20,
        default="review",
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job.title} - {self.user.username}"

    class Meta:
        unique_together = ("job", "user")
        ordering = ["-created_at"]


# 🔥 NEW MODEL (for multiple portfolio links)
class ApplicationLink(models.Model):
    LINK_TYPE_CHOICES = [
        ("github", "GitHub"),
        ("linkedin", "LinkedIn"),
        ("website", "Website"),
    ]

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="links",
    )

    link_type = models.CharField(
        max_length=20,
        choices=LINK_TYPE_CHOICES,
    )

    url = models.URLField()

    def __str__(self):
        return f"{self.link_type} - {self.url}"
