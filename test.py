from jobs.models import Job
from django.shortcuts import redirect
from users.services import can_apply_to_job

def test(request):
    jobs = Job.objects.filter(user=request.user).prefetch_related("applications").select_related('title')

    data = []

    for job in jobs:
        print(job.title)
    
    for category in job.categories.all():
        print(category.name)
    
    applications = job.applications.all()
    