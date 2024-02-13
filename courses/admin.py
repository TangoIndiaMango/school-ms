from django.contrib import admin

from courses.models import Course, CourseRegSettings, CourseRegistration

# Register your models here.
admin.site.register(
    (
        Course,
        CourseRegistration,
        CourseRegSettings,
    )
)
