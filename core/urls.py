from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar

urlpatterns = [
    path("admin/", admin.site.urls),
    path("jobboard/", include("jobboard.urls")),
    path("applications/", include("applications.urls")),
    path("users/", include("users.urls")),
    path("notifications/", include("notifications.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
