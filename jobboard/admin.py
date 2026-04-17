from django.contrib import admin
from .models import Job, UserRole

# Register your models here.
admin.site.register(Job)
admin.site.register(UserRole)