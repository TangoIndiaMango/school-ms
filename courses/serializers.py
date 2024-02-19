from rest_framework import serializers

from .models import Course, CourseRegistration


class CreateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"

class CourseRegSerializer(serializers.ModelSerializer):
    department_course = serializers.CharField(read_only=True)
    department_course_id = serializers.CharField(write_only=True)
    course_level = serializers.CharField(read_only=True)
    course_level_id = serializers.CharField(write_only=True)
    course_semester = serializers.CharField(read_only=True)
    course_semester_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = Course
        fields = "__all__"


class CourseUploadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Course
        fields = "__all__"



class GetCourseByDepartmentSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(read_only=True)
    course_name = serializers.CharField(read_only=True)
    level = serializers.CharField(read_only=True)

    class Meta:
        model = Course
        fields = "__all__"
        

class DepartmentCoursesSerializer(serializers.ModelSerializer):
    department = serializers.CharField(write_only=True)
    department_name = serializers.SerializerMethodField("get_departemnt")
    courses = serializers.CharField(read_only=True)
    level = serializers.CharField(write_only=True)
    levels = serializers.SerializerMethodField("get_levels")

    class Meta:
        model = Course
        fields = "__all__"
        
    def get_departemnt(self, obj):
        if obj.department.all():
            return obj.department.all().first().name
        return None
    
    def get_courses(self, obj):
        return [{"course_code": course.course_code, "course_name": course.course_name} for course in obj.courses.all()]
    
    def get_levels(self, obj):
        
        return obj.level.all().values_list("level", flat=True)


class GetCourseByLevelSerializer(serializers.ModelSerializer):
    courses = serializers.CharField(read_only=True)
    level = serializers.CharField(read_only=True)

    class Meta:
        model = Course
        fields = "__all__"



class CourseRegistarionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRegistration
        fields = "__all__"


class CourseResponseSerializer(serializers.ModelSerializer):
    course_level_name = serializers.StringRelatedField(source='course_level.level')
    course_semester_name = serializers.StringRelatedField(source='course_semester.name')
    department_course_name = serializers.StringRelatedField(source='department_course.name')

    class Meta:
        model = Course
        fields = ['id', 'course_code', 'course_name', 'course_description', 'course_credit', 'course_unit', 'course_status', 'mark', 'created_at', 'updated_at', 'course_level_name', 'course_semester_name', 'department_course_name']
