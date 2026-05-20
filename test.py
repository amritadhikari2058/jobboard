from jobs.models import Job
from django.shortcuts import redirect
from users.services import can_apply_to_job

def test(request):
    jobs = Job.objects.filter(user=request.user)

    for job in jobs:
        print(job.title)
    
    for category in job.categories.all():
        print(category.name)
    
    applications = job.applications.all()


def apply_to_job(request, job_id):
    job = Job.objects.get(id=job_id)

    if not can_apply_to_job(request.user, job):
        return redirect('job_detail', id=job_id)