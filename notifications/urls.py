from django.urls import path
from . import views

urlpatterns = [
    path("", views.notifications_view, name="notifications"),
    path(
        "read/<int:id>/",
        views.notifications_mark_as_read,
        name="notifications_mark_as_read",
    ),
    path("activity_logs/", views.activity_logs, name="activity_logs"),
]
