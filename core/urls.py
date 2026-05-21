from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("jobs.urls")),
    path(
        "applications/",
        include(("applications.urls", "applications"), namespace="applications"),
    ),
    path("users/", include("users.urls")),
    path("notifications/", include("notifications.urls")),
    path('login/', user_views.login_view, name='login'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
