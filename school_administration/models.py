from django.db import models


class Faculty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=20, unique=True)
    dean = models.OneToOneField(
        "users.DepartmentHead",
        on_delete=models.SET_NULL,
        null=True,
        related_name="dean",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    # save method such that we get the name then append Faculty before the name
    def save(self, *args, **kwargs):
        if not self.name.startswith("Faculty") and not self.name.startswith("School"):
            self.name = f"Faculty of {self.name}"
        super().save(*args, **kwargs)

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
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name="departments"
    )
    level = models.ForeignKey(
        "school_administration.Level",
        on_delete=models.SET_NULL,
        null=True,
        related_name="departments_level",
    )
    program_duration = models.CharField(max_length=50, null=True)
    qualification = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if not self.name.startswith("Department"):
            self.name = f"Department of {self.name}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f" ({self.short_name}) {self.name}"


class Level(models.Model):
    level = models.CharField(max_length=20, unique=True)
    staff_advisor_level = models.ForeignKey(
        "users.Lecturer",
        on_delete=models.SET_NULL,
        null=True,
        related_name="staff_advisor_level",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name}"
