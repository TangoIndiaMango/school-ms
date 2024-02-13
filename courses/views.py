from django.http import Http404
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from courses.models import CourseRegistration
from courses.utils import ProcessCourse
from school_administration.models import Department, Level
from schoolms.authentication_middleware import IsAuthenticatedCustom
from rest_framework.response import Response
from rest_framework import status
from users.user_permissions import IsAdminUser, IsStudent
import io
import csv
from django.db import transaction
from school_artifacts.models import Session, Semester
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .serializers import (
    CourseRegistarionSerializer,
    CourseResponseSerializer,
    CourseSerializer,
    Course,
    CourseUploadSerializer,
    GetCourseByDepartmentSerializer,
)

# Create your views here.


class CreateCourseView(ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = CourseResponseSerializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = CourseResponseSerializer(queryset, many=True)
    #     return Response(serializer.data)

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        # we want to be able to create a single course and also upload a csv file and create all the courses
        # in the csv file
        if "course_file" in request.FILES:
            file = request.FILES["course_file"]
            # unique_fields = ["course_code"]
            # result = create_courses_from_csv(
            #     file, CourseUploadSerializer, Course, unique_fields
            # )

            # if result:
            #     return Response(result, status=status.HTTP_200_OK)

            create_courses = ProcessCourse(file)
            response = create_courses.proces_data()
            if response:
                return response
        else:
            # just a single creation
            department_name = request.data.get("department_course_id", None)
            course_level = request.data.get("course_level_id", None)
            course_semester = request.data.get("course_semester_id", None)

            try:
                # Get department
                department = get_object_or_404(Department, name__iexact=department_name)

                # Get course level
                level = get_object_or_404(Level, level__iexact=course_level)

                # Get course semester
                semester = get_object_or_404(Semester, name__iexact=course_semester)

            except Http404 as e:
                return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

            # Update request data with department, level, and semester IDs
            request.data["department_course_id"] = department.id
            request.data["course_level_id"] = level.id
            request.data["course_semester_id"] = semester.id

            # Validate and save course
            course_serializer = self.serializer_class(data=request.data)
            course_serializer.is_valid(raise_exception=True)
            course_serializer.save()

            return Response(
                {"message": "Course created successfully."},
                status=status.HTTP_200_OK,
            )

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

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


class CourseRegistrationView(ModelViewSet):
    queryset = CourseRegistration.objects.all()
    serializer_class = CourseRegistarionSerializer
    permission_classes = (
        IsAuthenticatedCustom,
        IsStudent,
    )

    def create(self, request, *args, **kwargs):
        # Get active session and semester
        active_session = get_object_or_404(Session, is_active=True)
        active_semester = get_object_or_404(
            Semester, is_active=True, session=active_session
        )

        # Filter courses based on the active session and semester
        courses = Course.objects.filter(
            Q(course_semester=active_semester) | Q(course_semester__isnull=True),
            department=request.user.student.department,
        )

        # You can further filter courses based on any other criteria if needed

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Assign active session and semester to the course registration
        serializer.validated_data["session"] = active_session
        serializer.validated_data["semester"] = active_semester

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class GetCourseByDepartment(APIView):
    serializer_class = GetCourseByDepartmentSerializer
    permission_classes = (IsAuthenticatedCustom,)

    def get(self, request, *args, **kwargs):
        department_name = request.query_params.get("department_name").lower()
        courses = Course.objects.filter(department_course__name__iexact=department_name)
        serializer = CourseSerializer(courses, many=True)
        # we should check if we get data we display the data otherwise we display no courses in this department
        if not serializer.data:
            return Response(
                {"message": "No courses in this department"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.data, status=status.HTTP_200_OK)


# class AssignCourseToLecturer
