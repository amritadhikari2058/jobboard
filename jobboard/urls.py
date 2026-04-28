from django.urls import path
from . import views


urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("create/", views.create_job, name="create_job"),
    path("<int:id>/", views.job_detail, name="job_detail"),
    path("<int:id>/update/", views.update_job, name="update_job"),
    path("<int:id>/delete/", views.delete_job, name="delete_job"),
    path("recruiter_dashboard/", views.recruiter_dashboard, name="recruiter_dashboard"),
    path(
        "toggle_save_job/<int:job_id>/", views.toggle_save_job, name="toggle_save_job"
    ),
    path("saved-jobs/", views.saved_jobs_view, name="saved_jobs"),
    path("notifications/", views.notifications_view, name="notifications"),
    path(
        "notifications/read/<int:id>/",
        views.notifications_mark_as_read,
        name="notifications_mark_as_read",
    ),
    path("recruiter_dashboard/", views.recruiter_dashboard, name="recruiter_dashboard"),
    path("user_dashboard/", views.user_dashboard, name="user_dashboard"),
    path("activity_logs", views.activity_logs, name="activity_logs"),
    path("profile/edit/", views.edit_user_profile, name="edit_user_profile"),
    path(
        "profile/<str:username>/",
        views.view_user_profile,
        name="view_user_profile",
    ),
]
