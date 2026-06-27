from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
import debug_toolbar

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('home.urls')),
    path("project-1/", include("jobs.urls")),
    path(
        "project-1/applications/",
        include(("applications.urls", "applications"), namespace="applications"),
    ),
    path("project-1/users/", include("users.urls")),
    path("project-1/notifications/", include("notifications.urls")),
    path("login/", user_views.login_view, name="login"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]