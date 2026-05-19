from jobs.models import Job

def test(request):
    jobs = Job.objects.filter(user=request.user)

    for job in jobs:
        print(job.title)
    
    for category in job.categories.all():
        print(category.name)
    
    applications = job.applications.all()
    