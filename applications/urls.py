from django.urls import path
from . import views

urlpatterns = [
    path('', views.application_list, name='application_list'),

    # Application Routes
    path('<int:app_id>/', views.application_detail, name='application_detail'),
    path('<int:app_id>/update/', views.update, name='update_application'),
    path('<int:app_id>/delete/', views.delete, name='delete_application'),

    # Update Application Status
    path('<int:app_id>/accept/', views.accept_application, name='accept_application'),
    path('<int:app_id>/reject/', views.reject_application, name='reject_application'),

    # Job-based Route
    path('apply/<int:job_id>/', views.create, name='apply_application'),
]