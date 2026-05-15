from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("create/", views.create_job, name="create_job"),
    path("<int:id>/", views.job_detail, name="job_detail"),
    path("<int:id>/update/", views.update_job, name="update_job"),
    path("<int:id>/delete/", views.delete_job, name="delete_job"),
    path(
        "toggle_save_job/<int:job_id>/", views.toggle_save_job, name="toggle_save_job"
    ),
    path("saved-jobs/", views.saved_jobs_view, name="saved_jobs"),
    path("recruiter-jobs/", views.recruiter_jobs, name="recruiter_jobs"),
]
