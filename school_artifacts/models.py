from django.db import models

# Create your models here.
class Session(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    is_active = models.BooleanField(default=False)
    end_date = models.DateField()
    semesters = models.ManyToManyField("school_artifacts.Semester", related_name="sessions")
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class Semester(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name
