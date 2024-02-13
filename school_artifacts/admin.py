from django.contrib import admin

from .models import Semester, Session

# Register your models here.
admin.site.register(
    (
        Session,
        Semester,
    )
)
