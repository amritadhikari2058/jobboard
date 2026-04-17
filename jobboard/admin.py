from django.contrib import admin
from .models import Job, UserRole, SavedJob

# Register your models here.
admin.site.register(Job)
admin.site.register(UserRole)
admin.site.register(SavedJob)