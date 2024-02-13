from django.db import models


# Create your models here.
class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100)
    course_description = models.TextField()
    course_credit = models.IntegerField()
    course_unit = models.IntegerField()
    course_status = models.BooleanField(default=True)
    # department_course = models.ForeignKey("school_administration.Department", on_delete=models.CASCADE, related_name="course")
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
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    semester = models.ForeignKey('school_artifacts.Semester', on_delete=models.CASCADE)
    level = models.ForeignKey('school_administration.Level', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}" - "{}".format(self.student.matric_no, self.course.course_code)

    class Meta:
        ordering = ("-created_at",)
        
class CourseRegSettings(models.Model):
    course_reg_settings = models.ForeignKey(CourseRegistration, on_delete=models.CASCADE)
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
