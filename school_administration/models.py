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
    lecturers = models.ManyToManyField("users.Lecturer")
    students = models.ManyToManyField("users.Student")
    courses = models.ManyToManyField("courses.Course")
    department_head = models.OneToOneField(
        "users.Lecturer",
        on_delete=models.SET_NULL,
        null=True,
        related_name="department_head",
    )
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name="departments"
    )
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
    name = models.CharField(max_length=20, unique=True)
    level_courses = models.ManyToManyField("courses.Course")
    students = models.ManyToManyField("users.Student")
    level_department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="levels"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name}"
