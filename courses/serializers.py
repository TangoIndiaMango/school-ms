from rest_framework import serializers

from .models import Course, CourseRegistration


class CreateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"
        
class CourseRegistarionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRegistration
        fields = "__all__"
        