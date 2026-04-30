from django.urls import path
from . import views

urlpatterns = [
    path("edit/", views.edit_user_profile, name="edit_user_profile"),
    path(
        "<str:username>/",
        views.view_user_profile,
        name="view_user_profile",
    ),
    path("recruiter_dashboard/", views.recruiter_dashboard, name="recruiter_dashboard"),
    path("user_dashboard/", views.user_dashboard, name="user_dashboard"),
]
