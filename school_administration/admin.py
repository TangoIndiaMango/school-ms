from django.contrib import admin

from .models import Department, Faculty, Level

# Register your models here.
admin.site.register((Faculty, Department, Level))
