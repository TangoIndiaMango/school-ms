from django.db import models


# Create your models here.
class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    course_name = models.CharField(max_length=100, unique=True)
    course_description = models.TextField(blank=True, null=True)
    course_credit = models.IntegerField(default=0)
    course_unit = models.IntegerField(default=0)
    course_status = models.BooleanField(default=False)
    # course_prerequisite = models.ManyToManyField("self")
    mark = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.course_code)

    class Meta:
        ordering = ("-created_at",)


class CourseRegistration(models.Model):
    student = models.ForeignKey("users.Student", on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, related_name="courses")
    approved = models.BooleanField(default=False)
    semester = models.ForeignKey("school_artifacts.Semester", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}" - "{}".format(self.student.matric_no, self.semester.semester_name)

    class Meta:
        unique_together = ['student', 'semester']
        ordering = ("-created_at",)


class CourseRegSettings(models.Model):
    course_reg_settings = models.ForeignKey(
        CourseRegistration, on_delete=models.CASCADE
    )
    register_now = models.BooleanField(default=False)
    allow_debtor = models.BooleanField(default=False)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    late_reg_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.course_reg_settings.course.course_code)

    class Meta:
        ordering = ("-created_at",)


#  all courses a student is registered for...
# student_courses = CourseRegistration.objects.filter(student_id=student_id)
# all students registered for a specific course
# course_students = CourseRegistration.objects.filter(course_id=course_id)
