from rest_framework import serializers

from .models import Course, CourseRegistration


class CourseSerializer(serializers.ModelSerializer):
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
    department_name = serializers.CharField(
        source="department_course.name", read_only=True
    )

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
