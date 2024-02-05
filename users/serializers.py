from rest_framework import serializers
from users.models import CustomUser, Lecturer, Student


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

    # def create(self, validated_data):
    #     # get role-specific data
    #     matric_no = validated_data.pop("matric_no", None)
    #     staff_id = validated_data.pop("staff_id", None)
    #     department = validated_data.pop("department", None)
    #     level = validated_data.pop("level", None)
    #     faculty = validated_data.pop("faculty", None)

    #     # create user
    #     user = CustomUser.objects.create(**validated_data)

    #     # create role specif data
    #     if user.role == "student":
    #         Student.objects.create(
    #             user=user,
    #             matric_no=matric_no,
    #             department=department,
    #             level=level,
    #             faculty=faculty,
    #         )
    #     elif user.role == "staff":
    #         Lecturer.objects.create(
    #             user=user, staff_id=staff_id, department=department, faculty=faculty
    #         )

    #     return user


class UpdatePasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class StudentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(required=True)
    department = serializers.CharField(required=True)
    class Meta:
        model = Student
        fields = "__all__"
        depth = 1


class UpdateStudentSerializer(CustomUserSerializer):
    class Meta:
        model = Student
        fields = "__all__"


class LecturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecturer
        fields = "__all__"
