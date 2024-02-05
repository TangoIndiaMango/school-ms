from django.contrib import admin

from .models import Department, Faculty

# Register your models here.
admin.site.register((Faculty, Department,))