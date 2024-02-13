from django.db import models


class Faculty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=20, unique=True)
    dean = models.OneToOneField(
        "users.Lecturer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dean",
    )
    departments = models.ManyToManyField(
        "school_administration.Department", related_name="faculty", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    # save method such that we get the name then append Faculty before the name
    # def save(self, *args, **kwargs):
    #     if not self.name.startswith("Faculty") and not self.name.startswith("School"):
    #         self.name = f"Faculty of {self.name}"
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f" ({self.short_name}) {self.name}"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=20, unique=True)
    department_head = models.OneToOneField(
        "users.Lecturer",
        on_delete=models.SET_NULL,
        null=True,
        related_name="department_head",
    )
    level = models.ManyToManyField(
        "school_administration.Level",
    )
    courses = models.ManyToManyField("courses.Course", related_name="department", blank=True)
    students = models.ManyToManyField("users.Student", related_name="department", blank=True)
    lecturers = models.ManyToManyField("users.Lecturer", related_name="department", blank=True)
    program_duration = models.CharField(max_length=50, null=True)
    qualification = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    # def save(self, *args, **kwargs):
    #     if not self.name.startswith("Department"):
    #         self.name = f"Department of {self.name}"
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f" ({self.short_name}) {self.name}"


class Level(models.Model):
    level = models.CharField(max_length=20, unique=True)
    staff_advisor_level = models.ForeignKey(
        "users.Lecturer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_advisor_level",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.level}"
