from rest_framework import serializers

from users.models import Student
from .models import Faculty, Department, Level


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    levels = serializers.SerializerMethodField("get_levels")

    class Meta:
        model = Department
        fields = "__all__"

    def get_levels(self, obj):

        return obj.level.all().values_list("level", flat=True)


# class LevelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Level
#         fields = "__all__"


class LevelSerializer(serializers.ModelSerializer):
    courses_id = serializers.CharField(write_only=True, required=False)
    courses = serializers.SerializerMethodField("get_courses", read_only=True)
    department = serializers.SerializerMethodField("get_departemnt", read_only=True)

    class Meta:
        model = Level
        fields = "__all__"

    def get_departemnt(self, obj):
        if obj.department.all():
            return obj.department.all().first().name
        return None

    def get_courses(self, obj):
        return [
            {"course_code": course.course_code, "course_name": course.course_name}
            for course in obj.courses.all()
        ]


# class DepartmentSerializer(serializers.ModelSerializer):
#     levels = LevelSerializer(many=True, read_only=True)

#     class Meta:
#         model = Department
#         fields = "__all__"


class LevelResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = "__all__"


class StudentDepartmentSerializer(serializers.ModelSerializer):
    student_department = serializers.SerializerMethodField("get_department")
    user = serializers.SerializerMethodField("get_user")
    level = serializers.SerializerMethodField("get_level")

    class Meta:
        model = Student
        exclude = ("id",)

    def get_department(self, obj):
        department_name = obj.department.values_list("name", flat=True)
        return ", ".join(department_name)

    def get_user(self, obj):
        return str(obj.user)

    def get_level(self, obj):
        if obj.level:
            return obj.level.level
