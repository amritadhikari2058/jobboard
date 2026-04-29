from django.contrib import admin
from .models import Job, SavedJob, Category

# Register your models here.
admin.site.register(Job)
admin.site.register(SavedJob)
admin.site.register(Category)