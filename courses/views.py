from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from courses.models import CourseRegistration
from schoolms.authentication_middleware import IsAuthenticatedCustom
from rest_framework.response import Response
from rest_framework import status
from users.user_permissions import IsAdminUser
import io
import csv
from django.db import transaction
from utils.helpers import create_data_from_csv, match_dept_name

from .serializers import CourseRegistarionSerializer, CreateCourseSerializer, Course

# Create your views here.


class CreateCourseView(ModelViewSet):
    serializer_class = CreateCourseSerializer
    queryset = Course.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        # we want to be able to create a single course and also upload a csv file and create all the courses
        # in the csv file
        if "course_file" in request.FILES:
            file = request.FILES["course_file"]
            result = create_data_from_csv(file, self.serializer_class, Course)

            if result:
                return Response(result, status=status.HTTP_200_OK)
        else:
            # just a single creation
            department_name = request.data.get("department", None)
            if department_name:
                department, error = match_dept_name(department_name)
                if error:
                    return Response(error, status=status.HTTP_400_BAD_REQUEST)
                else:
                    request.data["department"] = department.id

            course_serializer = self.serializer_class(data=request.data)
            course_serializer.is_valid(raise_exception=True)
            self.perform_create(course_serializer)
            return Response(
                {
                    "message": "Course created successfully.",
                    "course": course_serializer.data,
                },
                status=status.HTTP_200_OK,
            )

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        course = self.get_object()
        course_serializer = self.serializer_class(course, data=request.data)
        course_serializer.is_valid(raise_exception=True)
        # course_serializer.save()
        self.perform_update(course_serializer)
        return Response(
            {
                "message": f"{course.course_code} updated successfully.",
                "course": course_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        course = self.get_object()
        self.perform_destroy(course)
        return Response(
            {
                "message": f"{course.course_code} deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


class RegisterCourseView(ModelViewSet):
    serializer_class = CourseRegistarionSerializer
    queryset = CourseRegistration.objects.all()
    permission_classes = (IsAuthenticatedCustom,)

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.create(serializer)
        return Response(
            {"message": "Course registered", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"message": "Course updated", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": f"{instance.name} deleted"},
            status=status.HTTP_200_OK,
        )
