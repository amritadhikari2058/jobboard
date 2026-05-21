from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "users"

urlpatterns = [
    path("edit/", views.edit_user_profile, name="edit_user_profile"),
    path("recruiter_dashboard/", views.recruiter_dashboard, name="recruiter_dashboard"),
    path("user_dashboard/", views.user_dashboard, name="user_dashboard"),
    path(
        "profile/<str:email>/",
        views.view_user_profile,
        name="view_user_profile",
    ),
    path("register/", views.register_view, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name='users/login.html'), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
