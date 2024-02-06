from django.db import IntegrityError, models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)

from school_administration.models import Department

# Create your models here.


ROLE_CHOICES = (
    ("student", "Student"),
    ("lecturer", "Lecturer"),
    ("dep_head", "Department Head"),
    ("dean", "Dean"),
    ("admin", "Admin"),
)

GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Female")
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        if not email:
            raise ValueError("Superuser must have an email address")

        if not password:
            raise ValueError("Superuser must have a password")

        user = self.create_user(email, password, **extra_fields)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=60, blank=True, null=True)
    residential_address = models.CharField(max_length=150, blank=True, null=True)
    home_address = models.CharField(max_length=150, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    objects = CustomUserManager()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # Role-based properties
    @property
    def is_student(self):
        return self.role == "student"

    @property
    def is_lecturer(self):
        return self.role == "lecturer"

    @property
    def is_dep_head(self):
        return self.role == "dep_head" if self.is_lecturer() else False

    @property
    def is_dean(self):
        return self.role == "dean" if self.is_lecturer() else False

    @property
    def is_admin(self):
        return self.is_superuser

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Student(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="student"
    )
    matric_no = models.CharField(max_length=50, unique=True)
    courses = models.ManyToManyField("courses.Course")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.matric_no}"


class Lecturer(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="lecturer"
    )
    staff_id = models.CharField(max_length=50, unique=True)
    designation = models.CharField(max_length=30, blank=True, null=True)
    courses = models.ManyToManyField("courses.Course")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.staff_id}"


class DepartmentHead(models.Model):
    lecturer = models.OneToOneField(
        Lecturer, on_delete=models.CASCADE, related_name="dep_head"
    )
    department = models.OneToOneField(
        Department, on_delete=models.CASCADE, related_name="dep_head"
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.department.name}"


# class Dean(models.Model):
#     lecturer = models.OneToOneField(Lecturer, on_delete=models.CASCADE, related_name='dep_head')
#     department = models.OneToOneField(Department, on_delete=models.CASCADE, related_name="dep_head")

#     def __str__(self):
#         return f"{self.user.first_name} {self.user.last_name} - {self.department.name}"


class VerificationUser(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="is_under_verification"
    )
    token = models.CharField(max_length=100)
    expiry = models.DateTimeField()
