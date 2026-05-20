from jobs.models import Job

def test(request):
    jobs = Job.objects.filter(user=request.user).prefetch_related("applications").select_related('title')

    data = []

    for job in jobs:
        total = job.applications.count()
        accepted = job.applications.filter(status="accepted").count()
        pending = job.applications.filter(status="pending").count()

        data.append({
            "title": job.title,
            "total": total,
            "accepted": accepted,
            "pending": pending,
        })
    