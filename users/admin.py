from django.contrib import admin

from .models import CustomUser, Lecturer, Student

# Register your models here.
admin.site.register((CustomUser, Student, Lecturer, ))
